'''Batch processor for the graph model'''
from config import includes
import json
import os
import extractor.extract as extract

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
    def batch_key_concept_extract(self, params):
        '''Main method for batch extraction of key concepts from the corpus to build the graph'''
        print("Batch Extract - Corpus Path:" , params)
        keyconceptdict = {}
        baseid = 10000


        # for every control in csf v2.0, build a mini corpus from GEN-AI concepts, run BERT+PatternRank to extract keyphrases
        # populate the dictionary with keyphrases
        # load the json file with an array of csf controls
        controldict = ioutil.load_json_to_dict(NodeType.CONTROL.label.lower() + "s", "name", NodeType.CONTROL.modelpath)
        print(len(controldict.keys()), " keys loaded from ", NodeType.CONTROL.modelpath)

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
            print ("Key phrases for Control: ", control)
            for res in result:
                print("Key phrases: ", res)
                keyname = res[0].replace(" ", "_")
                if keyname in keyconceptdict:                    
                    keyconceptdict[keyname]['controls'][control]=res[1]
                else:
                    keyconcept = KeyConceptNode(baseid + len(keyconceptdict), keyname, res[0])
                    keyconcept.setConceptConfidence(control, res[1])
                    keyconceptdict[keyname] = vars(keyconcept)
            
            # if controldict[control]['filecount'] == 0:
            #     print("Control: ", control, " has no files")
            
        ioutil.write_dict_to_json(keyconceptdict, includes.MODEL_BASE + "/keydict.tmp.json")
        return
    