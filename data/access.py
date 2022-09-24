from json import load, dump

config = "json/config.json"

def get_config()->dict:
    with open(config, 'r') as file:
        return load(file)

def set_config(overwrite_json)->None:
    with open(config, 'w') as file:
        dump(overwrite_json, file)

def get_default():
    with open("json/default.json", 'r') as file:
        return load(file)


def get_vwap():
    with open("json/vwap.json", 'r') as file:
        return load(file)


def get_values():
    with open("json/strategy.json", 'r') as file:
        return load(file)

def set_values(overwrite_json)->None:
    with open("json/strategy.json", 'w') as file:
        dump(overwrite_json, file)