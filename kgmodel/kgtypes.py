'''Module to Model definition for the CSF Knowledge Graph'''
from enum import Enum
import kgmodel.cypher as cypher


# Enumerations for the model
class NodeType(Enum):
    '''Model Node type enumeration'''
    def __init__(self, label, load):
        self.label = label
        self.load = load

    STANDARD='STANDARD', cypher.LOAD_STANDARD
    CONTROL='CONTROL', cypher.LOAD_CONTROL
    KEYCONCEPT='KEYCONCEPT', cypher.LOAD_STANDARD
    ASESSMENTQ='ASESSMENTQ', cypher.LOAD_STANDARD

class RelationType(Enum):
    '''Model relation type enumeration'''
    def __init__(self, label, load):
        self.label = label
        self.load = load

    HAS_CONTROL='HAS_CONTROL', cypher.LOAD_HAS_CONTROL
    MAPS_TO_='MAPS_TO',  cypher.LOAD_HAS_CONTROL
    CAPTURES='CAPTURES',  cypher.LOAD_HAS_CONTROL
    ASSESSES='ASSESSES',  cypher.LOAD_HAS_CONTROL
