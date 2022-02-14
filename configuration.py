import os
import yaml
import json

from paths import CONFIG_DIR, DATA_DIR

def read_config(name="config"):
    with open(os.path.join(CONFIG_DIR, name+".yaml"), "r") as f:
        data = yaml.safe_load(f.read())
    return data

def write_config(data, name="config"):
    with open(os.path.join(CONFIG_DIR, name+".yaml"), "w+") as f:
        f.write(yaml.dump(data, default_flow_style=False))

main_config = read_config()

def reload_config():
    global main_config
    main_config = read_config()

class CacheFile():
    def __init__(self, fp=os.path.join(DATA_DIR, "cache.json")):
        self.fp = fp
        if not os.path.exists(self.fp):
            self._write_to_file({})

    def _write_to_file(self, data):
        with open(self.fp, "w+") as f:
            f.write(json.dumps(data))

    def _read_from_file(self):
        with open(self.fp, "r") as f:
            data = json.loads(f.read())
        return data

    def set(self, key, value):
        data = self._read_from_file()
        data[key] = value
        self._write_to_file(data)

    def get(self, key):
        data = self._read_from_file()
        return data.get(key)


cache_file = CacheFile()