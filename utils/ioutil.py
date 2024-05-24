'''I/O utility functions for the kgraph modules.'''


import json


def load_json_to_dict(arraykey, dictkey, filename):
    '''Load and build node dictionary from a JSON'''
    dict = {}
    with open(filename, 'r') as f:
        data = json.load(f)
        for item in data[arraykey]:
            dict[item[dictkey]] = item

    return dict

def write_dict_to_json(dict, filename):
    '''Write a dictionary to a JSON file'''
    with open(filename, 'w') as f:
        json.dump(dict, f, indent=4)
    return