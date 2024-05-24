''' Description: Extract key terms from a text using KeyBERT'''
from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseCountVectorizer
from extractor import nlputils

class KeyTermExtractor(object):
    '''Extract key terms from a text using KeyBERT'''
    # Constructor
    def __init__(self, config):
        self.config = config
        if not self.config:
            # self.model = KeyBERT(model='all-MiniLM-L6-v2')
            self.model = KeyBERT(model='all-mpnet-base-v2')
        else:
            self.model = KeyBERT(model=config["model"])

#    "maxsum": {"enable":true,"candidates":20},
#    "mmr": {"enable":true, "diversity":0.5},
    def extract(self,buff):
        '''Main method for extracting keywords with KeyBERT defaults'''
        cbuff = nlputils.get_base_test(buff)
        if not self.config:
            keywords = self.model.extract_keywords(cbuff, keyphrase_ngram_range=(1, 3)
                , stop_words='english', use_maxsum=True, nr_candidates=20, use_mmr=True
                ,  diversity=0.5, top_n=10)
        else:
            keywords = self.model.extract_keywords(cbuff
                , keyphrase_ngram_range=(self.config["keyphrase_ngram_range"]["min"]
                , self.config["keyphrase_ngram_range"]["max"])
                , stop_words=self.config["stop_words"]
                , use_maxsum=self.config["maxsum"]["enable"]
                , nr_candidates=self.config["maxsum"]["candidates"]
                , use_mmr=self.config["mmr"]["enable"]
                , diversity=self.config["mmr"]["diversity"]
                , top_n=self.config["top_n"])
        return '', keywords
       
#    "maxsum": {"enable":true,"candidates":20},
#    "mmr": {"enable":true, "diversity":0.5},
    def extract_patternrank(self,buff):
        '''Main method for extracting keywords with KeyBERT and PatternRank'''
        cbuff = nlputils.get_base_test(buff)
        vectorizer = KeyphraseCountVectorizer()
    
        if not self.config:
            keywords = self.model.extract_keywords(cbuff
                , vectorizer=vectorizer, use_mmr=True, top_n=12)
        else:
            keywords = self.model.extract_keywords(cbuff
                , vectorizer=vectorizer
                , stop_words=self.config["stop_words"]
                , use_maxsum=self.config["maxsum"]["enable"]
                , nr_candidates=self.config["maxsum"]["candidates"]
                , use_mmr=self.config["mmr"]["enable"]
                , diversity=self.config["mmr"]["diversity"]
                , top_n=self.config["top_n"])
        return '', keywords