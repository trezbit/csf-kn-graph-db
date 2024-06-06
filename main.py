'''Main entry point for the application'''
import argparse
import os
import json
import extractor.extract as extract
import config.includes as includes
import connector.graphdb as graphdb
import gprocessor.process as process
import kgmodel.kgtypes as kgtypes
import infer.raggraph as raggraph

def extract_keyphrase(file,config):
    '''Extract keyphrases from a text file using KeyBERT'''
    print("Extract Key Phrase - File:", file, ", config: ", config)
    democfg = json.loads(config)
    if not democfg:
        with open(includes.KEYBERT_CONFIG, "r", encoding="utf-8") as f:
            democfg = json.load(f)
    berty = extract.KeyTermExtractor(democfg)
    text_file = open(file, "r", encoding="utf-8")
    sbuff = text_file.read()
    text_file.close()

    err, result = berty.extract(sbuff)
    if err != '' :
        print("Error: " + err )
        return
    for res in result:
        print("Key phrase: ", res)

def extract_keyphrase_patternrank(file,config):
    '''Extract keyphrases from a text file using KeyBERT'''
    print("Extract Key Phrase - File:", file, ", config: ", config)
    democfg = json.loads(config)
    # if not democfg:
    #     with open(includes.KEYBERT_CONFIG, "r", encoding="utf-8") as f:
    #         democfg = json.load(f)
    berty = extract.KeyTermExtractor(democfg)
    text_file = open(file, "r", encoding="utf-8")
    sbuff = text_file.read()
    text_file.close()

    err, result = berty.extract_patternrank(sbuff)
    if err != '' :
        print("Error: " + err )
        return
    for res in result:
        print("Key phrase: ", res)

def test_neo4j(params):
    '''Test Neo4j connectivity'''
    print("Test Neo4j connectivity - Config:", params)
    neocl = graphdb.NEO4JConnector()
    if params == '{}':
        neocl.verify_connectivity()
    elif params == 'clean':
        neocl.cleanup_full()
    elif params == 'loadcsv':
        process.GraphProcessor().build_graph()
    elif params == 'preprag':
        raggraph.GraphInference().graph_rag_prep()
    neocl.close()

def generate_key_concept_graph(params):
    '''Generate CSF key concept nodes and edges in JSON'''
    print("Generate CSF Key Concept Graph - Config:", params)

    process.GraphProcessor().build_keyconcept_subgraph(params)

    if os.path.exists(kgtypes.NodeType.KEYCONCEPT.modelpath):
        print("Key concept nodes and edges created at:", kgtypes.NodeType.KEYCONCEPT.modelpath)
    
    print("Completed running generate_key_concept_graph.")

def generate_assess_questionnaire_graph(params):
    '''Generate assessment questionnaire with question nodes and econtrol dges in JSON'''
    print("Generate Assessment Questionnaire Graph - Config:", params)

    process.GraphProcessor().build_assessment_questionnaire_subgraph(params)

    if os.path.exists(kgtypes.NodeType.ASESSMENTQ.modelpath):
        print("Assessment questionnaire nodes and edges created at:", kgtypes.NodeType.ASESSMENTQ.modelpath)
    
    print("Completed running generate_assess_questionnaire_graph.")

def export_kggraph_to_csv(params):
    '''Export CSF key concept nodes and edges to CSV'''
    process.GraphProcessor().export_standard_control_subgraph(params)
    print("Completed running export_standard_control_subgraph.")
    print("Export CSF key concept nodes and edges to CSV - Params:", params)
    process.GraphProcessor().export_keyconcept_subgraph(params)
    print("Completed running export_key_concept_graph_to_csv.")
    process.GraphProcessor().export_assessment_questionnaire_subgraph(params)
    print("Completed running export_assessment_questionnaire_graph_to_csv.")

def demo_infer_plain(question):
    '''Infer assessment questionnaire -- no augmentation for LLM'''
    if question is None:
        question = "What are some example questions for me to assess my organization for NIST CSF version 2.0 controls in GOVERN functional category?"
    print("Infer with question no augmentation for LLM - Question:", question)
    res = raggraph.GraphInference().infer_plain(question)
    reslist = res['answer'].split('\n')
    print("ChatGPT inference result: ")
    for r in reslist:
        print(r)

def demo_infer_rag(question):
    '''Infer assessment questionnaire -- with KG augmentation for LLM'''
    if question is None:
        question = "What are some example questions for me to assess my organization for NIST CSF version 2.0 controls in GOVERN functional category?"
    print("Infer with question KG augmentation for LLM - Question:", question)
    res = raggraph.GraphInference().infer_rag(question)
    # print json result with newlines as a list
    reslist = res['answer'].split('\n')
    print("ChatGPT rag-inference result: ")
    for r in reslist:
        print(r)
    


def parse_args():
    '''CLI Argument parser for the application'''
    parser = argparse.ArgumentParser(description='CSF knowledge graph KG build utilities and query demos')
    subparser = parser.add_subparsers(dest='command')

    kwext = subparser.add_parser('extract', help='KeyPhrase(from text) extraction testing: KeyBERT vs KeyBERT+PatternRank')
    csfmod = subparser.add_parser('csfmod', help='CSF KG build utilities for Assessment Questionnaire, Key Concept and Control/Standard Subgraphs')

    tester = subparser.add_parser('tester', help='KG tester utilities for Neo4j and other LLM connectivity testing')
    inferer = subparser.add_parser('infer', help='Graph + RAG inference demonstrations')


    convertgroup1 = kwext.add_mutually_exclusive_group(required=True)
    convertgroup1.add_argument('--patternrank'
                               , help='Extract keyphrases from corpus document with optional parameters using patternrank vectorizer'
                               , nargs='?', const='{}', type=str)
    convertgroup1.add_argument('--keyphrase'
                               , help='Extract Keyphrases corpus document with optional parameters'
                               , nargs='?', const='{}', type=str)
    kwext.add_argument('--file', help='Filepath', type=str, required=True)

    convertgroup2 = tester.add_mutually_exclusive_group(required=True)
    convertgroup2.add_argument('--neo4j'
                               , help='Test Neo4j connectivity'
                               , nargs='?', const='{}', type=str)
    convertgroup2.add_argument('--openai'
                               , help='Test OpenAI connectivity'
                               , nargs='?', const='{}', type=str)
    
    convertgroup3 = csfmod.add_mutually_exclusive_group(required=True)
    convertgroup3.add_argument('--keyconcept'
                               , help='Generate CSF key concept nodes and edges in JSON with optional parameters'
                               , nargs='?', const='{}', type=str)
    convertgroup3.add_argument('--assess'
                               , help='Generate assessment questionnaire with question nodes and econtrol dges in JSON with optional parameters'
                               , nargs='?', const='{}', type=str)
    
    convertgroup3.add_argument('--tocsv', help='Dump JSON CSF nodes and edges to CSV with optional parameters'
                               , nargs='?', const='{}', type=str)

    csfmod.add_argument('--outdir', help='File written to directory', type=str, required=False)

    convertgroup4 = inferer.add_mutually_exclusive_group(required=True)
    convertgroup4.add_argument('--plain', help='Issue a plain LLM chain query'
                               , nargs='?', const='{}', type=str)
    convertgroup4.add_argument('--rag', help='Issue a retrieval augmented LLM chain query'
                               , nargs='?', const='{}', type=str)
    
    inferer.add_argument('--question', help='Question for LLM', type=str, required=False)
    
    args = parser.parse_args()
    return args

def run_session (args):
    '''Run session for the application'''
    #pprint.pprint(args)
    if args.command is None:
        print("Undefined utility test command. Options: extract, csfmod")
    elif (args.command == 'extract' and args.patternrank is not None):
        extract_keyphrase_patternrank(args.file, args.patternrank)
    elif (args.command == 'extract' and args.keyphrase is not None):
        extract_keyphrase(args.file, args.keyphrase)
    elif (args.command == 'csfmod' and args.keyconcept is not None):
        generate_key_concept_graph(args.keyconcept)
    elif (args.command == 'csfmod' and args.assess is not None):
        generate_assess_questionnaire_graph(args.assess)
    elif (args.command == 'csfmod' and args.tocsv is not None):
        # csf2csv(args.file, args.txt)
        export_kggraph_to_csv(args.tocsv)
    elif (args.command == 'tester' and args.neo4j is not None):
        test_neo4j(args.neo4j)
    elif (args.command == 'tester' and args.openai is not None):
        print("Open AI connectivity tester not implemented.")
    elif (args.command == 'infer' and args.plain is not None):
        demo_infer_plain(args.question)
    elif (args.command == 'infer' and args.rag is not None):
        demo_infer_rag(args.question)
    else:
        print("Unknown utility test command option for: "    , args.command)
    print("\nEnd of demo session...", args.command)

if __name__ == '__main__':
    builder_args = parse_args()
    run_session(builder_args)
