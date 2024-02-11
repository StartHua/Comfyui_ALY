# from .mine_nodes import *
from .ALY_Seg_Cloth import *
from .ALY_Seg_Obj import * 
from .ALY_Seg_head import *
from .ALY_Seg_Skin import * 

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "ALY_Seg_Cloth":ALY_Seg_Cloth,
    "ALY_Seg_Obj":ALY_Seg_Obj,
    "ALY_Seg_head":ALY_Seg_head,
    "ALY_Seg_Skin":ALY_Seg_Skin
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "ALY_Seg_Cloth":"ALY_Seg_Cloth",
    "ALY_Seg_Obj":"ALY_Seg_Obj",
    "ALY_Seg_head":"ALY_Seg_head",
    "ALY_Seg_Skin" : "ALY_Seg_Skin"
}
