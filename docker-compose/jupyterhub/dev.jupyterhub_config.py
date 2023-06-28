import os
from shared_jupyterhub_config import *

# Only config unique to a local dev setup should be placed here
# Create a dictionary of volumes to be passed into set_shared_traitlets
# vols = {"localFolderPath:MountFolderPath"}
vols = {}

# Nearly all config can be put in shared_jupyterhub_config.py
set_shared_traitlets(c, vols)
