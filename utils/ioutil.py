'''I/O utility functions for the kgraph modules.'''


import json
import csv




def load_json_to_dict(arraykey, dictkey, filename):
    '''Load and build node dictionary from a JSON'''
    dict = {}
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            for item in data[arraykey]:
                dict[item[dictkey]] = item
    except Exception as e:
        print("Error: ", e, "File: ", filename)
        return None
    return dict

def write_dict_to_json(dict, filename):
    '''Write a dictionary to a JSON file'''
    with open(filename, 'w') as f:
        json.dump(dict, f, indent=4)
    return

def graph_jsondata_to_csv(arraykey,injson,outcsv):
    '''Convert JSON data to CSV'''
    print("Converting JSON data to CSV: ", injson, " to ", outcsv, ", array key: ", arraykey)
    with open(injson) as json_file:
        jsondata = json.load(json_file)

    data_file = open(outcsv, 'w', newline='')
    csv_writer = csv.writer(data_file,quoting=csv.QUOTE_NONNUMERIC,doublequote=True)

    count = 0
    for data in jsondata[arraykey]:
        if count == 0:
            header = data.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(data.values())

    data_file.close()
    return