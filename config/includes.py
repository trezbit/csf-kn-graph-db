'''Module to define constants and config functions for the project'''
import os
from pathlib import Path
from enum import Enum
import configparser


ROOT_DIR = os.path.abspath(Path(__file__).parent.parent)
KEYBERT_CONFIG=os.path.abspath(Path(__file__).parent) + "/keybert.json"

# Corpus, mappings, samples
MODEL_CORPUS_BASE= ROOT_DIR + "/corpus"

# Model IO files
MODEL_BASE= ROOT_DIR + "/kgmodel"
MODEL_JSON_NODES= MODEL_BASE + "/nodes"
MODEL_JSON_RELATIONS= MODEL_BASE + "/edges"
MODEL_CSV_BASE= MODEL_BASE + "/csv"



# Graph data public sets -- for cloud graph db access
PUBLIC_GRAPH_DATA_ROOT = "https://raw.githubusercontent.com/trezbit/csf-kn-graph-db/master/kgmodel/csv"


# Constants
class CorpusType(Enum):
    '''Corpus type enumeration'''
    def __init__(self, ctype, path):
        self.type = ctype
        self.path = path

    ASSESS='assessment-questionnaire', MODEL_CORPUS_BASE + '/assess/questions'
    CORE='core-csf', MODEL_CORPUS_BASE + '/csf-core/keys'
    MAPS_2_0='mappings-v2-0', MODEL_CORPUS_BASE + '/map-v2.0'
    MAPS_1_1='mappings-v1-1', MODEL_CORPUS_BASE + '/map-v1.1'


# config utils
def get_config(config, section=''):
    '''Return configuration element'''
    section_config = {}
    if (section != '' and config.has_section(section)):
        items = config.items(section)
        for item in items:
            iarray = item[1].split(",")
            if len(iarray) > 0:      
                section_config[item[0]] = iarray
            else:
                section_config[item[0]] = item[0]
    return section_config

def load_config_full(filename):
    '''Load configuration from file'''
    config=configparser.ConfigParser()
    config.read(filename)

    fullcfg = {}
    for section in config.sections():
        fullcfg[section]=get_config(config,section)
    return fullcfg
