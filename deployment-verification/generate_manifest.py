import json
import os
import subprocess
import datetime

# wraps the data gathered by a function in some extra information:
# - file path
# - success/fail at collecting data
# - exception raised (if any)
def manifest_collect_method(fn):
    def _internal(self, entry_name, *args, **kwargs):
        if os.path.exists(entry_name):
            # this is a file, so change the name to its path
            entry_id = os.path.basename(entry_name)
        else:
            # this is something else
            entry_id = entry_name
        
        # make a new entry in the manifest collector
        file_manifest = self.new_entry(entry_id)

        try:
            # fill data with result from decorated function
            file_manifest["data"] = fn(self, entry_name, *args, **kwargs)
        except Exception as e:
            # note failure, but continue
            file_manifest["success"] = False
            file_manifest["data"] = {
                "exception": str(e)
            }

        return file_manifest

    return _internal

class ManifestCollector():
    def __init__(self):
        # manifest_data will be a JSON-like object for now
        self.manifest_data = { }

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
        # simple enough: return json data
        with open(json_file) as f:
            json_data = json.load(f)
            for pathent in path:
                json_data = json_data[pathent]

        return json_data

    # gets the git hash of the opal-ops repo
    @manifest_collect_method
    def from_git(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"git repository at {path} does not exist")

        # current commit hash
        result_hash = subprocess.check_output(
            ["git", "-C", path, "rev-parse", "HEAD"]
        )
        # current commit tag (empty if this commit has no tag)
        result_tag = subprocess.check_output(
            ["git", "-C", path, "tag", "--points-at", "HEAD"]
        )
        tag = result_tag.decode("ascii").strip()
        if not tag:
            tag = "[WARNING] no tag for this commit"

        return {
            "hash": result_hash.decode("ascii").strip(),
            "tag": tag
        }

    def collect_file(self, filename, *args, **kwargs):
        filename = os.path.abspath(filename)
        if filename.endswith(".env"): 
            # intentionally doesn't allow .env.secrets
            result = self.from_env_file(filename)
        elif filename.endswith(".json"):
            result = self.from_json(filename)
        elif filename.endswith(".git"):
            # assume it's a git repo
            result = self.from_git(os.path.dirname(filename))
        result["path"] = filename

    @manifest_collect_method
    def collect_dict(self, name, data):
        return data

    def to_json(self):
        return json.dumps(self.manifest_data, indent=4)


if __name__ == '__main__':
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="generate_manifest",
        description="generate a json manifest from files"
    )

    parser.add_argument('files', type=str, nargs='+',
        help="Files to collect into the manifest"
    )

    parser.add_argument('--extra', type=str,
        help=(
            "json object of extra information to manually add"
            " to the deployment manifest"
        )
    )

    args = parser.parse_args()

    # quick and dirty cli
    mc = ManifestCollector()
    for arg in args.files:            
        mc.collect_file(arg)

    if args.extra:
        extra_data = json.loads(args.extra)
        mc.collect_dict("extra_info", extra_data)

    print(mc.to_json())
