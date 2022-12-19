import json
import os
import subprocess

# wraps the data gathered by a function in some extra information:
# - file path
# - success/fail at collecting data
# - exception raised (if any)
def manifest_collect_method(fn):
    def _internal(self, entry_name, *args, **kwargs):
        if os.path.exists(entry_name):
            # this is a file
            entry_id = os.path.basename(entry_name)
        else:
            entry_id = entry_name
        
        try:
            file_manifest = self.new_entry(entry_id)
        except FileNotFoundError:
            return

        try:
            file_manifest["data"] = fn(self, entry_name, *args, **kwargs)
        except Exception as e:
            file_manifest["success"] = False
            file_manifest["data"] = {
                "exception": str(e)
            }

        return file_manifest

    return _internal

class ManifestCollector():
    def __init__(self):
        # manifest_data will be a JSON-like object for now
        self.manifest_data = {}

    def new_entry(self, entry_name):
        # prep dict entry for data in this file
        self.manifest_data[entry_name] = {}
        self.manifest_data[entry_name]["success"] = True
        self.manifest_data[entry_name]["data"] = {}
        return self.manifest_data[entry_name]

    # collect environment variables from an env file
    # default: gets all environment variables
    @manifest_collect_method
    def from_env_file(self, env_file, keys=[], exclude=["password"]):
        manifest_data = {}

        # extract environment variables from file
        with open(env_file) as f:
            for line in f:
                # skip comments and empty lines
                if line.startswith("#") or not line.strip():
                    continue
                env_name, env_val = line.strip().split("=")
                # censor some environment variables
                if any([e in env_name.lower() for e in exclude]):
                    manifest_data[env_name] = "**********"
                    continue
                # some env vars have quotes
                env_val = env_val.strip(" \"'") 
                env_name = env_name.strip()
                if any([env_name == k for k in keys]) or not keys:
                    manifest_data[env_name] = env_val

        # fill missing keys with empty string
        for k in keys:
            if k not in manifest_data:
                manifest_data[k] = "[ERROR] Not Defined"

        return manifest_data
                
    # collect information from a json file
    # path: path to json element to collect (default is everything)
    @manifest_collect_method
    def from_json(self, json_file, path=[]):
        with open(json_file) as f:
            json_data = json.load(f)
            for pathent in path:
                json_data = json_data[pathent]

        return json_data

    # gets the git hash of the opal-ops repo
    @manifest_collect_method
    def from_git(self, unused):
        result = subprocess.check_output(["git", "rev-parse", "HEAD"])
        hash = result.decode("ascii").strip()
        return { "opal-ops" : hash }

    def collect_file(self, filename, *args, **kwargs):
        if filename.endswith(".env"): 
            # intentionally doesn't allow .env.secrets
            result = self.from_env_file(filename)
        elif filename.endswith(".json"):
            result = self.from_json(filename)
        result["file_path"] = filename

    def to_json(self):
        return json.dumps(self.manifest_data, indent=4)


if __name__ == '__main__':
    import sys
    
    # quick and dirty cli
    mc = ManifestCollector()
    for arg in sys.argv[1:]:
        if arg == "-h":
            print("Usage: python generate_manifest.py [files]")
            print("file types supported: .env, .json")
            exit()
            
        mc.collect_file(arg)
    mc.from_git("git")

    print(mc.to_json())
