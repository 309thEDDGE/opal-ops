import deepdiff

def env_to_dict(file):
    out = {}
    for line in file:
        parts = line.split("=")
        parts = [ part.strip() for part in parts ]
        out[parts[0]] = parts[1]
    return out

def compare_env(file1, file2):
    with open(file1) as f1, open(file2) as f2:
        d1 = env_to_dict(f1)
        d2 = env_to_dict(f2)
    return deepdiff.DeepDiff(d1, d2)

if __name__ == "__main__":
    import sys
    print(compare_env(sys.argv[1], sys.argv[2]))