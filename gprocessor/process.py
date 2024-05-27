'''Batch processor for the graph model'''
from config import includes
import json
import os
import extractor.extract as extract
import extractor.nlputils as nlputils

from kgmodel.kgtypes import NodeType, RelationType
from kgmodel.kgmodel import KeyConceptNode
from kgmodel.kgmodel import QuestionNode

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

        self.build_node(NodeType.KEYCONCEPT)
        self.build_node(NodeType.ASESSMENTQ)
        self.build_relation(RelationType.CAPTURES)
        self.build_relation(RelationType.ASSESSES)
        
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
    
    def batch_questionnaire_extract(self, controldict):
        '''Main method for batch load of scoped questions from the corpus to build the graph'''
        print("Batch Extract - Corpus Path:", includes.CorpusType.CORE.path)

        assessquestionaire = {}
        baseid = 50000

        # for every control in csf v2.0, extract questions from OpenAI generated assessment questionaires
        # populate the dictionary with questions
        for control in controldict:
            # iterate through the JSON files in the corpus directory beginning with the control name
            # compile core considerations from the assessment corpus
            assessqfile = includes.CorpusType.ASSESS.path + "/" + control + ".json"
            # check if the file exists
            if os.path.isfile(assessqfile):
                questiondict = ioutil.load_json_to_dict("results", "question", assessqfile)
            else:
                print("Assessment Questionnaire file: ", assessqfile, " not found for control: ", control)
                return
            #print ("Assessment Questionnaire for Control: ", control, "via file: ", assessqfile)
            for quest in questiondict:
                # print("Assessment Question: ", quest)
                if quest in assessquestionaire:                    
                    assessquestionaire[quest]['controls'][control]=1
                else:
                    newquest = QuestionNode(baseid + len(assessquestionaire), quest)
                    newquest.setScope(questiondict[quest]['scope'])
                    newquest.setRationale(questiondict[quest]['rationale'])
                    newquest.controls[control]=1
                    assessquestionaire[quest]=vars(newquest)

        return assessquestionaire
    
    def build_assessment_questionnaire_subgraph (self,params={}):
        '''Main method for building the assessment questionnaire subgraph'''
        print("Build Assessment Questionnaire Subgraph")

        # load the json file with an array of csf controls
        controldict = ioutil.load_json_to_dict(NodeType.CONTROL.arraykey, "name", NodeType.CONTROL.modelpath)
        print(len(controldict.keys()), " keys loaded from ", NodeType.CONTROL.modelpath)
        assessmentqdict = self.batch_questionnaire_extract(controldict)
        ioutil.write_dict_to_json(assessmentqdict, includes.MODEL_BASE + "/assess.subgraph.json")

        #build the question nodes
        questionnodedict = {NodeType.ASESSMENTQ.arraykey:[]}
        questionedgedict = {RelationType.ASSESSES.arraykey:[]}
        for quest in assessmentqdict:
            node = {"id":assessmentqdict[quest]['id']
                    , "name":assessmentqdict[quest]['name']
                    , "scope":assessmentqdict[quest]['scope']
                    , "rationale":assessmentqdict[quest]['rationale']}
            questionnodedict[NodeType.ASESSMENTQ.arraykey].append(node)
            for control in assessmentqdict[quest]['controls']:
                edge = {"from_id": assessmentqdict[quest]['id']
                        , "to_id":controldict[control]['id']
                        , "strength":assessmentqdict[quest]['controls'][control]}
                questionedgedict[RelationType.ASSESSES.arraykey].append(edge)

        ioutil.write_dict_to_json(questionnodedict, NodeType.ASESSMENTQ.modelpath)
        ioutil.write_dict_to_json(questionedgedict, RelationType.ASSESSES.modelpath)
        return
    
    def export_assessment_questionnaire_subgraph(self, params={}):
        '''Main method for exporting the assessment questionnaire subgraph to csv for upload to cloud graph db'''
        print("Export Assessment Questionnaire nodes and edges to CSV")
        # export the key concept subgraph (node) to a cloud storage
        ioutil.graph_jsondata_to_csv(NodeType.ASESSMENTQ.arraykey, NodeType.ASESSMENTQ.modelpath, includes.MODEL_CSV_BASE 
                                     + "/" + NodeType.ASESSMENTQ.label.lower() + ".csv")
        ioutil.graph_jsondata_to_csv(RelationType.ASSESSES.arraykey, RelationType.ASSESSES.modelpath, includes.MODEL_CSV_BASE 
                                     + "/" + RelationType.ASSESSES.label.lower() + ".csv")
        
        return
    def export_standard_control_subgraph(self, params={}):
        '''Main method for exporting the assessment questionnaire subgraph to csv for upload to cloud graph db'''
        print("Export Assessment Questionnaire nodes and edges to CSV")
        # export the standard and control (nodes) to a cloud storage
        ioutil.graph_jsondata_to_csv(NodeType.STANDARD.arraykey, NodeType.STANDARD.modelpath, includes.MODEL_CSV_BASE 
                                     + "/" + NodeType.STANDARD.label.lower() + ".csv")
        ioutil.graph_jsondata_to_csv(NodeType.CONTROL.arraykey, NodeType.CONTROL.modelpath, includes.MODEL_CSV_BASE 
                                     + "/" + NodeType.CONTROL.label.lower() + ".csv")
        ioutil.graph_jsondata_to_csv(RelationType.HAS_CONTROL.arraykey, RelationType.HAS_CONTROL.modelpath, includes.MODEL_CSV_BASE 
                                     + "/" + RelationType.HAS_CONTROL.label.lower() + ".csv")
        ioutil.graph_jsondata_to_csv(RelationType.MAPS_TO.arraykey, RelationType.MAPS_TO.modelpath, includes.MODEL_CSV_BASE 
                                     + "/" + RelationType.MAPS_TO.label.lower() + ".csv")    
        return
    