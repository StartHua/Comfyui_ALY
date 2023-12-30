
MAX_RESOLUTION=8192

from typing import List

from .AlyVision import imagese
from alibabacloud_imageseg20191230.client import Client
from alibabacloud_imageseg20191230.models import SegmentClothAdvanceRequest
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_util.models import RuntimeOptions


import os
import io
import sys
import re
import json
import time
import torch
import psutil
import random
import datetime
import comfy.sd
import comfy.utils
import numpy as np
import folder_paths
import comfy.samplers
import latent_preview
import comfy.model_base
from pathlib import Path
import comfy.model_management
from urllib.request import urlopen
from collections import defaultdict
from PIL.PngImagePlugin import PngInfo
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Optional, Tuple, Union, Any
import nodes
from PIL import Image,ImageOps

from .utils import *

comfy_path = os.path.dirname(folder_paths.__file__)
custom_nodes_path = os.path.join(comfy_path, "custom_nodes")



class CXH_ALY_Seg_Cloth:
   
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":
                {
                "cloth_type":   (["None","tops", "coat","skirt","pants","bag","shoes","hat"],{"default":"None"}  ),     
                "image_path": ("STRING",{"default": "","multiline": False}), 
                "return_form":   (["whiteBK", "mask"],{"default":"mask"} ),     
                }
        }

    RETURN_TYPES = ("IMAGE","IMAGE")
    RETURN_NAMES = ("source","class")
    OUTPUT_NODE = True
    FUNCTION = "sample"
    CATEGORY = "CXH"

    def sample(self,cloth_type,image_path,return_form):
    
        if not os.path.exists(image_path):
            print("文件不存在:" + image_path)
            return
        im = open(image_path, 'rb')

        segment_cloth_request = SegmentClothAdvanceRequest()
        segment_cloth_request.image_urlobject =im
        #设置子类
        if cloth_type != "None":
            segment_cloth_request.cloth_class = [cloth_type]
        #返回类型    
        if return_form != "PNG":
            segment_cloth_request.return_form = return_form
            
        runtime = RuntimeOptions()
        try:
            # 初始化Client
            client = imagese.create_client_json()
            response = client.segment_cloth_advance(segment_cloth_request, runtime)
            image_url = response.body.data.elements[0].image_url
            class_url = response.body.data.elements[1].class_url
            other_cloth = None
            if cloth_type != "None" :
               other_cloth = class_url[cloth_type]
            print("输出:")
            print(image_url)
            print(other_cloth)
        except Exception as error:
            # 获取整体报错信息
            print(error)
            # 获取单个字段
            print(error.code)
            
        source_img = img_from_url(image_url)
        if other_cloth == None:
            oImage = img_from_url(image_url)
        else:
            oImage =img_from_url(other_cloth)
        return (source_img,oImage)