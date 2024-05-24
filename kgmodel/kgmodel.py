'''CSF Knowfledge Graph Model Definitions'''
import os
import json
from .kgtypes import NodeType, RelationType


# make all CSF objects JSON friendly
class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class ModelBase(object):
    def __init__(self, id, name, typedef):
        self.id = id
        self.name = name
        self.typedef = typedef
    def setName(self, name):
        self.name = name
    def getName(self):
        return self.name
    def getDict(self):
        return self.__dict__
    def setId(self, id):
        self.id = id
    def getId(self):
        return self.id  
    def getTypeDef(self):
        return self.typedef
    
class ControlNode(ModelBase):
    # Constructor
    def __init__(self, id, name, functional_category):
        self.nodetype = NodeType.CONTROL
        self.functional_category = functional_category
        ModelBase.__init__(self,id, NodeType.CONTROL.label)
    
    def getFunctionalCategory(self):
        return self.functional_category

    def addKeyPhraseRef(self, refid):
        if not refid in self.keyphrases:
            self.keyphrases.append(refid)

class StandardNode(ModelBase):
    # Constructor
    def __init__(self, id, name,display_name,role):
        self.display_name = display_name
        self.role = role
        ModelBase.__init__(self,id, name, NodeType.STANDARD.label)
    
    def getDisplayName(self):
        return self.display_name
    def setDisplayName(self, display_name):
        self.display_name = display_name
    def setRole(self, role):
        self.role = role
    def getRole(self):
        return self.role

class KeyConceptNode(ModelBase):
    # Constructor
    def __init__(self, id, name):
        self.accronym = ""
        self.occurrence = 1
        self.controls = {}
        ModelBase.__init__(self,id, name, NodeType.KEYCONCEPT.label)
    
    def setAccronym(self, accronym):
        self.accronym = accronym
    def getAccronym(self):
        return self.accronym
    def incrementOccurrence(self, byamnt=1):
        self.occurrence += byamnt

    def setConceptConfidence(self, controlkey,confidence):
        self.controls[controlkey] = confidence
    def getConceptConfidence(self, controlkey): 
        return self.controls[controlkey]
    def getCorpusConfidenceMean(self):
        # statiscal mean of the confidence values
        return sum(self.controls.values())/len
    def getCorpusConfidenceMedian(self):
        # statiscal median of the confidence values
        median= sorted(self.controls.values())[len(self.controls.values())//2]
        return median
    def getCorpusConfidenceMax(self):
        # statiscal max of the confidence values
        return max(self.controls.values())
    def getCorpusConfidenceMin(self):
        # statiscal min of the confidence values
        return min(self.controls.values())

