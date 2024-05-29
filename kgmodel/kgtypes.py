'''Module to Model definition for the CSF Knowledge Graph'''
from enum import Enum
import kgmodel.cypher as cypher
import config.includes as includes


# Enumerations for the model
class NodeType(Enum):
    '''Model Node type enumeration'''
    def __init__(self, label, load,modelpath,arraykey):
        self.label = label
        self.load = load
        self.modelpath = modelpath
        self.arraykey = arraykey

    STANDARD='STANDARD', cypher.LOAD_STANDARD, includes.MODEL_JSON_NODES + "/standard.json", 'standards'
    CONTROL='CONTROL', cypher.LOAD_CONTROL, includes.MODEL_JSON_NODES + "/csf-v2.0-controls.json", 'controls'
    KEYCONCEPT='KEYCONCEPT', cypher.LOAD_KEYCONCEPT, includes.MODEL_JSON_NODES + "/keyconcept.json", 'keyconcepts'
    ASESSMENTQ='QUESTION', cypher.LOAD_ASSESSMENTQ, includes.MODEL_JSON_NODES + "/question.json", 'questions'

class RelationType(Enum):
    '''Model relation type enumeration'''
    def __init__(self, label, load, modelpath, arraykey):
        self.label = label
        self.load = load
        self.modelpath = modelpath
        self.arraykey = arraykey

    HAS_CONTROL='HAS_CONTROL', cypher.LOAD_HAS_CONTROL, includes.MODEL_JSON_RELATIONS + "/has_control.json", 'standard_controls'
    MAPS_TO='MAPS_TO',  cypher.LOAD_MAPS_TO, includes.MODEL_JSON_RELATIONS + "/control_map.json", 'maps_to'
    CAPTURES='CONTROL_CAPTURES',  cypher.LOAD_CONTROL_CAPTURES, includes.MODEL_JSON_RELATIONS + "/capture.json", 'captures'
    ASSESSES='ASSESSES',  cypher.LOAD_ASSESSES_CONTROL, includes.MODEL_JSON_RELATIONS + "/assesses.json", 'assesses'
