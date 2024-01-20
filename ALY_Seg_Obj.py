
MAX_RESOLUTION=8192

from typing import List

from .AlyVision import imagese
from alibabacloud_imageseg20191230.models import SegmentCommodityRequest
from alibabacloud_tea_util.models import RuntimeOptions

import os
import datetime
import numpy as np
import folder_paths
import comfy.model_base
from pathlib import Path
from urllib.request import urlopen
from collections import defaultdict
from PIL.PngImagePlugin import PngInfo
from PIL import Image, ImageDraw, ImageFont
import nodes

from .utils import *

comfy_path = os.path.dirname(folder_paths.__file__)
custom_nodes_path = os.path.join(comfy_path, "custom_nodes")



class ALY_Seg_Obj:
   
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":
                {   
                    "image":("IMAGE", {"default": "","multiline": False}),   
                }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("obj",)
    OUTPUT_NODE = True
    FUNCTION = "sample"
    CATEGORY = "CXH"

    def sample(self,image):
        
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        folder_path = os.path.join(custom_nodes_path,"Comfyui_ALY","cache",f"{date_str}.jpg")

        # 零时缓存转换成阿里io.buff
        save_tensor_image(image,folder_path)
        
        imp1 = open(folder_path, 'rb')
        
        segment_commodity_request = SegmentCommodityRequest()
        segment_commodity_request.image_urlobject =imp1
            
        runtime = RuntimeOptions()
        try:
            # 初始化Client
            client = imagese.create_client_json()
            response = client.segment_commodity_with_options_async(segment_commodity_request, runtime)
            print(response)
            image_url = response.body.data.image_url
            print(image_url)
        except Exception as error:
            # 获取整体报错信息
            print(error)
            # 获取单个字段
            print(error.code)
            
        source_img = img_from_url(image_url)
        return (source_img)