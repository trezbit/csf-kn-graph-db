'''Main entry point for the application'''
import argparse
import json
import extractor.extract as extract
import config.includes as includes
import connector.graphdb as graphdb

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

def test_neo4j(config):
    '''Test Neo4j connectivity'''
    print("Test Neo4j connectivity - Config:", config)
    neocl = graphdb.NEO4JConnector()
    neocl.verify_connectivity()
    neocl.close()


def parse_args():
    '''CLI Argument parser for the application'''
    parser = argparse.ArgumentParser(description='CSF knowledge graph build utilities')
    subparser = parser.add_subparsers(dest='command')

    kwext = subparser.add_parser('extract', help='KeyPhrase(from text) Extraction')
    csfmod = subparser.add_parser('csfmod', help='Demo functionality for CSF taxonomy extraction')

    tester = subparser.add_parser('tester', help='Graph database utilities')

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
    convertgroup3.add_argument('--json'
                               , help='Build CSF taxonomy as JSON with optional parameters'
                               , nargs='?', const='{}', type=str)
    convertgroup3.add_argument('--csv', help='Build CSF taxonomy as CSV with optional parameters'
                               , nargs='?', const='{}', type=str)
    csfmod.add_argument('--outdir', help='File written to directory', type=str, required=True)

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
    elif (args.command == 'csfmod' and args.json is not None):
        print("Graph model build utility not implemented.")
    elif (args.command == 'csfmod' and args.csv is not None):
        # csf2csv(args.file, args.txt)
        print("Graph model build utility not implemented.")
    elif (args.command == 'tester' and args.neo4j is not None):
        test_neo4j(args.neo4j)
    elif (args.command == 'tester' and args.openai is not None):
        # csf2csv(args.file, args.txt)
        print("Open AI connectivity tester not implemented.")
    else:
        print("Unknown utility test command option for: "    , args.command)
    print("\nEnd of demo session...", args.command)

if __name__ == '__main__':
    builder_args = parse_args()
    run_session(builder_args)
