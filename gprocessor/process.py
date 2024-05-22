'''Batch processor for the graph model'''
from config import includes
from kgmodel.kgtypes import NodeType, RelationType
from connector.graphdb import NEO4JConnector
from kgmodel.cypher import CREATE_CONSTRAINT


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
        # self.build_node(NodeType.KEYCONCEPT)
        # self.build_node(NodeType.QUESTION)
        # self.build_relation(RelationType.IN_STANDARD.reltype, RelationType.IN_STANDARD.from_node, RelationType.IN_STANDARD.to_node, RelationType.IN_STANDARD.props)
        # self.build_relation(RelationType.MAPPED_TO_CONTROL.reltype, RelationType.MAPPED_TO_CONTROL.from_node, RelationType.MAPPED_TO_CONTROL.to_node, RelationType.MAPPED_TO_CONTROL.props)
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
    
    def build_relation(self, direction, reltype, props):
        '''Main method for building relations for batch upload'''
        print("Build Relations - Direction:", direction, ", Type: ", reltype, ", Properties (dict): ", props)

        return
    def batch_key_concept_extract(self, corpuspath):
        '''Main method for batch extraction of keyphrases'''
        print("Batch Extract - Corpus Path:", corpuspath)
        
        # for every file in corpuspath:

            # extract_keyphrase(file, self.config)
        return
    