'''Batch processor for the graph model'''
from config import includes
import json
import os
import extractor.extract as extract
import extractor.nlputils as nlputils

from kgmodel.kgtypes import NodeType, RelationType
from kgmodel.kgmodel import KeyConceptNode

from connector.graphdb import NEO4JConnector
from kgmodel.cypher import *
from utils import ioutil


class GraphProcessor():
    '''Batch node/relation processor for the graph model'''
    # Constructor
    def __init__(self, config={}):
        self.config = config
        self.connector = NEO4JConnector()

    # Destructor
    def __del__(self):
        self.connector.close()

    def cleanup_graph(self):
        '''Main method for cleaning up the graph'''
        print("Cleanup Graph")
        self.connector.cleanup_full()
        return
    
    def build_graph(self):
        '''Main method for building the graph'''
        print("Build Graph")
        self.cleanup_graph()
        self.build_node(NodeType.STANDARD)
        self.build_node(NodeType.CONTROL)
        self.build_relation(RelationType.HAS_CONTROL)
        self.build_relation(RelationType.MAPS_TO)

        # self.build_node(NodeType.KEYCONCEPT)
        # self.build_node(NodeType.QUESTION)
        # self.build_relation(RelationType.CAPTURES_CONTROL.reltype, RelationType.CAPTURES_CONTROL.from_node, RelationType.CAPTURES_CONTROL.to_node, RelationType.CAPTURES_CONTROL.props)
        # self.build_relation(RelationType.ASSESSES_CONTROL.reltype, RelationType.ASSESSES_CONTROL.from_node, RelationType.ASSESSES_CONTROL.to_node, RelationType.ASSESSES_CONTROL.props)
        return
    
    def build_node(self, nodetype:NodeType):
        '''Main method for building nodes for batch upload'''
        print("Build Nodes - Label:", nodetype.load)
        newconst = CREATE_CONSTRAINT.replace("__LABEL__", nodetype.label)
        self.connector.run_query(newconst)
        self.connector.run_query(nodetype.load)
        
        return
    
    def build_relation(self, reltype:RelationType):
        '''Main method for building relations for batch upload'''
        print("Build Relations -  Type: ", reltype)
        self.connector.run_query(reltype.load)

        return
    def refine_key_concepts_extract(self, dict, threshold=0.35):
        '''Helper method for refining key concepts'''
        print("Refine Key Concepts")

        keyconceptdict = {}

        for kp in dict:
            minthreshold = max(dict[kp]['controls'].values())
            # print ("Key Concept: ", kp, " Controls: ", dict[kp]['controls'], minthreshold)
            #meanthreshold = sum(kp['controls'].values())/len(kp['controls'].values())
            #medianthreshold = sorted(keyconceptdict[kp]['controls'].values())[len(kp['controls'].values())//2]

            if(nlputils.is_common_kgkeyterm(kp, minthreshold, threshold)) or (minthreshold <= 0.1):
                print("Excluding: ", kp)
                continue
            else:
                keyconceptdict[kp] = dict[kp]
        return keyconceptdict
    
    
    def batch_key_concept_extract(self, controldict):
        '''Main method for batch extraction of key concepts from the corpus to build the graph'''
        print("Batch Extract - Corpus Path:", includes.CorpusType.CORE.path)
        keyconceptdict = {}
        baseid = 10000

        # for every control in csf v2.0, build a mini corpus from GEN-AI concepts, run BERT+PatternRank to extract keyphrases
        # populate the dictionary with keyphrases

        for control in controldict:
            # iterate through the JSON files in the corpus directory beginning with the control name
            controldict[control]['filecount'] =0
            buffer = []

            # compile key areas from the csf-core corpus
            for file in os.listdir(includes.CorpusType.CORE.path):
                if file.startswith(control):
                    #print("Processing file: ", file)
                    controldict[control]['filecount'] += 1
                    keydict = ioutil.load_json_to_dict("results", "key_concept", includes.CorpusType.CORE.path + "/" + file)
                    for key, value in keydict.items():
                        buffer.append(value["key_concept"])

            # compile core considerations from the assessment corpus
            assessqfile = includes.CorpusType.ASSESS.path + "/" + control + ".json"
            # check if the file exists
            if os.path.isfile(assessqfile):
                controldict[control]['filecount'] += 1
                scopedict = ioutil.load_json_to_dict("results", "scope", assessqfile)
                buffer.append(scopedict.keys())

            berty = extract.KeyTermExtractor({})
            err, result = berty.extract_patternrank("\n".join(buffer))
            if err != '' :
                print("Error: " + err )
                return
            # print ("Key phrases for Control: ", control)
            for res in result:
                # print("Key phrases: ", res)
                keyname = res[0]
                # Check if the key concept is an acronym or has an acronym
                is_or_has_abbr, acronym, keyname = nlputils.is_or_has_kgaccronym(res[0])
                      
                if keyname in keyconceptdict:                    
                    keyconceptdict[keyname]['controls'][control]=res[1]
                    keyconceptdict[keyname]['occurrence'] += 1
                    if is_or_has_abbr:
                        keyconceptdict[keyname]['accronym'] = acronym  
                else:
                    keyconcept = KeyConceptNode(baseid + len(keyconceptdict), keyname)
                    keyconcept.setConceptConfidence(control, res[1])
                    keyconcept.setAccronym(acronym)
                    keyconceptdict[keyname]=vars(keyconcept)

                    

            
            # if controldict[control]['filecount'] == 0:
            #     print("Control: ", control, " has no files")
            
        # refine the key concepts
        refineddict = self.refine_key_concepts_extract(keyconceptdict)


        return refineddict
    
    def build_keyconcept_subgraph(self, params={}):
        '''Main method for building the key concept graph with key concepts and controls as nodes and CAPTURES as edges'''
        print("Build Key Concept Graph Base Model")
        # load the json file with an array of csf controls
        controldict = ioutil.load_json_to_dict(NodeType.CONTROL.arraykey, "name", NodeType.CONTROL.modelpath)
        print(len(controldict.keys()), " keys loaded from ", NodeType.CONTROL.modelpath)

        keyconceptdict = self.batch_key_concept_extract(controldict)
        # nlputils.exclude_common_keys(keywords)
        ioutil.write_dict_to_json(keyconceptdict, includes.MODEL_BASE + "/keyconcept.subgraph.json")

        #build the key concept nodes
        keyconceptnodedict = {NodeType.KEYCONCEPT.arraykey:[]}
        keyconceptedgedict = {RelationType.CAPTURES.arraykey:[]}
        for keyconcept in keyconceptdict:
            node = {"id":keyconceptdict[keyconcept]['id']
                    , "name":keyconceptdict[keyconcept]['name']
                    , "accronym":keyconceptdict[keyconcept]['accronym']}
            keyconceptnodedict[NodeType.KEYCONCEPT.arraykey].append(node)
            for control in keyconceptdict[keyconcept]['controls']:
                edge = {"from_id":controldict[control]['id']
                        , "to_id":keyconceptdict[keyconcept]['id']
                        , "confidence":keyconceptdict[keyconcept]['controls'][control]}
                keyconceptedgedict[RelationType.CAPTURES.arraykey].append(edge)

        ioutil.write_dict_to_json(keyconceptnodedict, NodeType.KEYCONCEPT.modelpath)
        ioutil.write_dict_to_json(keyconceptedgedict, RelationType.CAPTURES.modelpath)
        #build the key concept CAPTURES controls edges
        
        return
    
    def export_keyconcept_subgraph(self, params={}):
        '''Main method for exporting the key concept subgraph to csv for upload to cloud graph db'''
        print("Export Key Concept nodes and edges to CSV")
        # export the key concept subgraph (node) to a cloud storage
        ioutil.graph_jsondata_to_csv(NodeType.KEYCONCEPT.arraykey, NodeType.KEYCONCEPT.modelpath, includes.MODEL_CSV_BASE + "/" + NodeType.KEYCONCEPT.label.lower() + ".csv")
        
        # export the key concept subgraph (edge) to a cloud storage
        ioutil.graph_jsondata_to_csv(RelationType.CAPTURES.arraykey, RelationType.CAPTURES.modelpath, includes.MODEL_CSV_BASE + "/" + RelationType.CAPTURES.label.lower() + ".csv")
        return
    