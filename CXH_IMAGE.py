
MAX_RESOLUTION=8192

from typing import List

from .AlyVision import imagese
from alibabacloud_imageseg20191230.client import Client
from alibabacloud_imageseg20191230.models import SegmentClothAdvanceRequest
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_util.models import RuntimeOptions

from .utils import *

import os
import sys
import torch
import comfy.utils
import numpy as np
import folder_paths
from pathlib import Path
from PIL import Image,ImageOps

comfy_path = os.path.dirname(folder_paths.__file__)
custom_nodes_path = os.path.join(comfy_path, "custom_nodes")

class CXH_IMAGE:
   
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":
                {
                  "file_path": ("STRING",{"multiline": False,"default": ""})     
                }
        }

    RETURN_TYPES = ("IMAGE","STRING")
    RETURN_NAMES = ("image","path")
    OUTPUT_NODE = True
    FUNCTION = "sample"
    CATEGORY = "CXH"

    def sample(self,file_path):
        if not os.path.exists(file_path):
            print("文件不存在:" + file_path)
            return
        im = img_from_path(file_path)
        return (im,file_path)

