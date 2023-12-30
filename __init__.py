# from .mine_nodes import *
from .CXH_GPT import *
from .CXH_ALY_Seg_Cloth import *
from .CXH_IMAGE import *

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "CXH_GPT":CXH_GPT,
    "CXH_ALY_Seg_Cloth":CXH_ALY_Seg_Cloth,
    "CXH_IMAGE":CXH_IMAGE
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "CXH_GPT": "CXH_GPT",
    "CXH_ALY_Seg_Cloth":"CXH_ALY_Seg_Cloth",
    "CXH_IMAGE":"CXH_IMAGE"
}
