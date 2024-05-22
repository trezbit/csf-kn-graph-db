'''Batch processor for the graph model'''
from config import includes

class GraphProcessor():
    '''Batch node/relation processor for the graph model'''
    # Constructor
    def __init__(self, config={}):
        self.config = config

    def build_nodes(self, label, props):
        '''Main method for building nodes for batch upload'''
        print("Build Nodes - Label:", label, ", Properties: ", props)
        return
    def build_relations(self, direction, reltype, props):
        '''Main method for building relations for batch upload'''
        print("Build Relations - Direction:", direction, ", Type: ", reltype, ", Properties (dict): ", props)

        return
    def batch_key_concept_extract(self, corpuspath):
        '''Main method for batch extraction of keyphrases'''
        print("Batch Extract - Corpus Path:", corpuspath)
        
        # for every file in corpuspath:

            # extract_keyphrase(file, self.config)
        return
    