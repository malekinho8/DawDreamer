import numpy as np
import matplotlib.pyplot as plt
import librosa as lb
import librosa.display as lbd
import os
import random
import json
import xmltodict
import difflib
import re
import math

def read_txt(path: str) -> str:
    """
    Read the contents of a text file and return as a string.
    
    Args:
        path (str): The path to the text file to be read.
    
    Returns:
        str: The contents of the text file as a string.
    """
    with open(path, 'r') as file:
        txt = file.read()
    return txt

def parse_helm_file():
    # specify the filepath
    filepath = 'examples/helm_synth_sound_rendering/helm_parameter_info.txt'

    # Regular expression to match ValueDetails
    pattern = re.compile(r'\{ \"(.+?)\", (.*?), (.*?),')
    
    # Dict to store parameter details
    param_dict = {}
    
    lines = read_txt(filepath)
    
    # Just try to match the ValueDetails keyword
    matches = pattern.findall(lines)
        
    for match in matches:
        param_name = match[0]
        min_val = float(match[1])
        max_val = float(match[2])
        param_dict[param_name] = (min_val, max_val)
            
    return param_dict

def normalize_helm_preset(param_dict, preset_dict):
    normalized_dict = {}

    for param, value in preset_dict.items():
        if param in param_dict:
            min_val, max_val = param_dict[param]
            # normalize value to [0, 1] range
            normalized_value = (value - min_val) / (max_val - min_val)
            normalized_dict[param] = normalized_value
    
    return normalized_dict

def make_helm_json_parameter_mapping(plugin, preset_path:str, json_preset_folder=f'helm_json_presets', verbose=True):
    """
    Read a preset file in XML format, apply the settings to the plugin, and create a JSON file
    that maps the preset parameters to the plugin parameters.
    
    Args:
        plugin (dawdreamer.PluginProcessor): The plugin to which the preset settings will be applied.
        preset_path (str): The path to the preset file in XML format.
        verbose (bool): if True, it will print parameter mapping. Default is True.
    
    Returns:
        str: The name of the JSON file containing the parameter mapping.
    """
    # create the json preset folder if it does not already exist
    if not os.path.exists(json_preset_folder):
        os.mkdir(json_preset_folder)

    # specify the output json filename
    preset_name = preset_path.split(os.sep)[-1].split('.')[0]
    output_name = f'{json_preset_folder}{os.sep}helm-{preset_name}-parameter-mapping.json'

    # obtain the parameter dictionary
    param_dict = parse_helm_file()

    if not os.path.exists(output_name):
        # read the XML preset path
        preset_settings = read_txt(preset_path)

        # apply the synth preset settings to the synth plugin processor object
        parameter_mapping = {}

        # Load JSON settings
        settings = json.loads(preset_settings)

        # Extract the program settings
        json_keys = normalize_helm_preset(param_dict, settings["settings"])

        # Get the parameters description from the plugin
        parameters = plugin.get_parameters_description()

        # Create a dictionary with parameter names as keys and their indices as values
        param_name_to_index = {param["name"]: param["index"] for param in parameters}

        # Iterate over each JSON key
        for key in json_keys:
            # specify the exceptions to map manually
            if key in param_name_to_index.keys():
                # Extract the value of the JSON key from the JSON string using regex
                param_value = json_keys[key]
                index = param_name_to_index[key]
                parameter_mapping[key] = {'match': key, 'value': param_value, 'index': index}
            else:
                print(f'Key {key} was not found in DawDreamer mapping dictionary. Continuing...')
        
        with open(output_name, 'w') as outfile:
            json.dump(parameter_mapping, outfile)  

    return output_name    

def load_helm_preset(dawdreamer_plugin,parameter_mapping_json):
    """
    Load a preset into a plugin using a JSON file that maps preset parameters to plugin parameters.
    
    Args:
        dawdreamer_plugin (dawdreamer.PluginProcessor): The plugin to which the preset settings will be applied.
        parameter_mapping_json (str): The path to the JSON file that maps preset parameters to plugin parameters.
    Returns:
        dawdreamer.PluginProcessor: The plugin with the preset settings applied.
    """
    # Load JSON file into a dictionary
    with open(parameter_mapping_json, 'r') as infile:
        parameter_map = json.load(infile)

    # Get the parameters description from the plugin
    parameters = dawdreamer_plugin.get_parameters_description()

    # Iterate over each JSON key
    for key in parameter_map.keys():
        dawdreamer_plugin.set_parameter(parameter_map[key]['index'], parameter_map[key]['value'])
    
    return dawdreamer_plugin