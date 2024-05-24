'''Module to Model definition for the CSF Knowledge Graph'''
from enum import Enum
import kgmodel.cypher as cypher
import config.includes as includes


# Enumerations for the model
class NodeType(Enum):
    '''Model Node type enumeration'''
    def __init__(self, label, load,modelpath):
        self.label = label
        self.load = load
        self.modelpath = modelpath

    STANDARD='STANDARD', cypher.LOAD_STANDARD, includes.MODEL_JSON_NODES + "/standard.json"
    CONTROL='CONTROL', cypher.LOAD_CONTROL, includes.MODEL_JSON_NODES + "/csf-v2.0-controls.json"
    KEYCONCEPT='KEYCONCEPT', cypher.LOAD_STANDARD, includes.MODEL_JSON_NODES + "/keyconcept.json"
    ASESSMENTQ='ASESSMENTQ', cypher.LOAD_STANDARD, includes.MODEL_JSON_NODES + "/questions.json"

class RelationType(Enum):
    '''Model relation type enumeration'''
    def __init__(self, label, load):
        self.label = label
        self.load = load

    HAS_CONTROL='HAS_CONTROL', cypher.LOAD_HAS_CONTROL
    MAPS_TO='MAPS_TO',  cypher.LOAD_MAPS_TO
    CAPTURES='CAPTURES',  cypher.LOAD_HAS_CONTROL
    ASSESSES='ASSESSES',  cypher.LOAD_HAS_CONTROL
