import os
from string import Template

template_path = "/opt/opal/conf/metaflow_config.json"
output_path = "/home/jovyan/.metaflowconfig/config.json"

with open(template_path, "r") as f:
    template = Template(f.read())

with open(output_path, "w") as f:
    f.write(template.safe_substitute(os.environ))
