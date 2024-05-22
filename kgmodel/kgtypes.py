'''Module to Model definition for the CSF Knowledge Graph'''
from enum import Enum
import kgmodel.cypher as cypher


# Enumerations for the model
class NodeType(Enum):
    '''Model Node type enumeration'''
    def __init__(self, label, load):
        self.label = label
        self.load = load

    STANDARD='standard', cypher.LOAD_STANDARD
    CONTROL='control', cypher.LOAD_STANDARD
    KEYCONCEPT='keyconcept', cypher.LOAD_STANDARD
    QUESTION='question', cypher.LOAD_STANDARD

class RelationType(Enum):
    '''Model relation type enumeration'''
    def __init__(self, reltype, from_node, to_node, props):
        self.reltype = reltype
        self.from_node = from_node
        self.to_node = to_node

        self.props = props
    IN_STANDARD='in_standard', NodeType.CONTROL.label, NodeType.STANDARD.label, {"from_id":0,"to_id":0,"strenght":0.0}
    MAPPED_TO_CONTROL='mapto_control',  NodeType.CONTROL.label,  NodeType.CONTROL.label, {"from_id":0,"to_id":0,"strenght":0.0}
    CAPTURES_CONTROL='capture_control',  NodeType.KEYCONCEPT.label,  NodeType.CONTROL.label, {"from_id":0,"to_id":0,"strenght":0.0}
    ASSESSES_CONTROL='assess_control',  NodeType.QUESTION.label,  NodeType.CONTROL.label, {"from_id":0,"to_id":0,"strenght":0.0}