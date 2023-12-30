
MAX_RESOLUTION=8192

import os
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

comfy_path = os.path.dirname(folder_paths.__file__)
custom_nodes_path = os.path.join(comfy_path, "custom_nodes")

N_Nodes_path = os.path.join(custom_nodes_path, "ComfyUI-N-Nodes-main\py")
sys.path.append(N_Nodes_path)
import gptcpp_node as N_nodes


class CXH_GPT:
   
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":
                {
                "gpt_model": (folder_paths.get_filename_list("GPTcheckpoints"),), #GPT 模型
                "story": ("STRING", {"default": "Positive","multiline": True}),   #小说内容
                
                "max_tokens": ("INT", {"default": 2048, "min": 0, "max": 4096, "step": 2048}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0, "max": 1, "step": 0.01}),
                
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"), ),   #图片模型
                "vae_name": (["Baked VAE"] + folder_paths.get_filename_list("vae"),),
                "clip_skip": ("INT", {"default": -1, "min": -24, "max": 0, "step": 1}),
                
                "lora1_name": (["None"] + folder_paths.get_filename_list("loras"),),
                "lora1_model_strength": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "lora1_clip_strength": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),

                "lora2_name": (["None"] + folder_paths.get_filename_list("loras"),),
                "lora2_model_strength": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "lora2_clip_strength": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),

                "lora3_name": (["None"] + folder_paths.get_filename_list("loras"),),
                "lora3_model_strength": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "lora3_clip_strength": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                
                "positive": ("STRING", {"default": "Positive","multiline": True}),
                "negative": ("STRING", {"default": "Negative", "multiline": True}),
                "empty_latent_width": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "empty_latent_height": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),        

                 "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                 "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                 "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),  #采样器
                 "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                 "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                 # "input_image": ("IMAGE",),        
                }
        }

    RETURN_TYPES = ( "VAE", "CLIP", "IMAGE","STRING","CONDITIONING","CONDITIONING","MODEL")
    RETURN_NAMES = ("vae", "vaeclip", "image","string","POSITIVE", "NEGATIVE","MODEL")
    OUTPUT_NODE = True
    FUNCTION = "sample"
    CATEGORY = "CXH"

    def sample(self, 
                       gpt_model,max_tokens,temperature,story,
                       ckpt_name, vae_name, clip_skip,
                       lora1_name, lora1_model_strength, lora1_clip_strength,
                       lora2_name, lora2_model_strength, lora2_clip_strength, 
                       lora3_name, lora3_model_strength, lora3_clip_strength, 
                       positive,
                       negative,
                       empty_latent_width, empty_latent_height, seed, 
                       steps,
                       cfg,
                       sampler_name,
                       scheduler,
                       denoise):
        #GPT推理
        gpt_positive = self.GPT_Pos(gpt_model,story,max_tokens,temperature)
        gpt_positive_list = gpt_positive.split('@###@')   
        gpt_positive_list = [x for x in gpt_positive_list if x!= '']
        # print("GPT:")
        # print(gpt_positive)    

        #空 Latent节点：size = 1 (后面是一个循环)
        latent = torch.zeros([1, 4, empty_latent_height // 8, empty_latent_width // 8]).cpu()
        samples = {"samples":latent}
        
        #加载模型
        model,clip,vae = self.load_ckpt(ckpt_name)
        
        # 加载lora
        if lora1_name != "None":
            model, clip = self.load_lora(lora1_name, model, clip, lora1_model_strength, lora1_clip_strength)

        if lora2_name != "None":
            model, clip = self.load_lora(lora2_name, model, clip, lora2_model_strength, lora2_clip_strength)

        if lora3_name != "None":
            model, clip = self.load_lora(lora3_name, model, clip, lora3_model_strength, lora3_clip_strength)

        # Check for custom VAE
        if vae_name != "Baked VAE":
            vae = self.load_vae(vae_name)
           
        #正向提示词用于输出
        output_positive = "masterpiece, best quality, high resolution," + positive
        t_positive_tokens = clip.tokenize(output_positive)
        t_ckpt_positive_cond, t_ckpt_positive_pooled = clip.encode_from_tokens(
                                    t_positive_tokens, return_pooled=True)
        t_positive_output = [[t_ckpt_positive_cond, {"pooled_output": t_ckpt_positive_pooled}]]   
        
        #反向提示词
        negative_tokens = clip.tokenize(negative)
        ckpt_negative_cond, ckpt_negative_pooled = clip.encode_from_tokens(negative_tokens, return_pooled=True)
        negative_output = [[ckpt_negative_cond, {"pooled_output": ckpt_negative_pooled}]]
        
        #遍历组合提示词
        samples_list = []
        for gpt_item in gpt_positive_list:
            output_positive = "masterpiece, best quality, high resolution," + positive + gpt_item
            # 处理提示词
            positive_tokens = clip.tokenize(output_positive)
            ckpt_positive_cond, ckpt_positive_pooled = clip.encode_from_tokens(
                                    positive_tokens, return_pooled=True)
            positive_output = [[ckpt_positive_cond, {"pooled_output": ckpt_positive_pooled}]]
            samp_samples = self.common_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive_output, negative_output, samples, denoise=denoise)
            #图片
            latent = samp_samples["samples"]
            samp_images = vae.decode(latent).cpu()
            samples_list.append(samp_images)
        print("图片数量:" +str(len(samples_list)))
        output_image = torch.cat(samples_list, 0)

        return (vae,clip,output_image,gpt_positive,t_positive_output,negative_output,model)
    
    # 加载GPT生成提示词
    def GPT_Pos(self,gpt_model,story,max_tokens,temperature):
       # GPTLoaderSimple
        gpu_layers = 27
        n_threads = 8
        max_ctx = 2048
        gpt_model, gpt_model_path = N_nodes.GPTLoaderSimple().load_gpt_checkpoint(
            gpt_model, gpu_layers, n_threads, max_ctx)
               
        # GPTSampler
        top_p = 0.5
        logprobs = 0
        echo = "disable"
        stop_token = "STOPTOKEN"
        frequency_penalty = 0.0
        presence_penalty = 0.0
        repeat_penalty = 1.17647
        top_k = 40
        tfs_z = 1.0
        print_output = "disable"
        cached = "NO"
        prefix = "### Instruction: "
        suffix = "### Response: "
        
        # p1 = self.prompt.replace("number", str(screen))
        # GPT_Story = p1.replace("content",story)
        # print("=======")
        # print(GPT_Story)
        gpt_answer = N_nodes.GPTSampler().generate_text(story, max_tokens, temperature, 
                top_p, logprobs, echo, stop_token, frequency_penalty, presence_penalty, repeat_penalty, 
                top_k, tfs_z, gpt_model, gpt_model_path, print_output, cached, prefix, suffix) 
        gpt_positive = gpt_answer["result"][0] 
        # print("==============")
        # print(gpt_positive)
        return gpt_positive
    
     # 加载模型
    def load_ckpt(self,ckpt_name):
       
        ckpt_path = folder_paths.get_full_path("checkpoints", ckpt_name)
        loaded_ckpt = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"))
        
        model, clip, vae =  loaded_ckpt[0], loaded_ckpt[1], loaded_ckpt[2]
        return model,clip,vae
    
    #加载lora
    def load_lora(self, lora_name, model, clip, strength_model, strength_clip):
        model_hash = str(model)[44:-1]
        clip_hash = str(clip)[25:-1]

        unique_id = f'{model_hash};{clip_hash};{lora_name};{strength_model};{strength_clip}'

        lora_path = folder_paths.get_full_path("loras", lora_name)
        lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
        model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength_model, strength_clip)
        
        return model_lora, clip_lora    
    
    #加载vae解码器
    def load_vae(self, vae_name):
        vae_path = folder_paths.get_full_path("vae", vae_name)
        sd = comfy.utils.load_torch_file(vae_path)
        loaded_vae = comfy.sd.VAE(sd=sd)
        
        return loaded_vae
    
    # 采集
    def common_ksampler(self, model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent, denoise=1.0, disable_noise=False, start_step=None, last_step=None, force_full_denoise=False, preview_latent=True, disable_pbar=False):
        
        device = comfy.model_management.get_torch_device()
        
        latent_image = latent["samples"]

        if disable_noise:
            noise = torch.zeros(latent_image.size(), dtype=latent_image.dtype, layout=latent_image.layout, device="cpu")
        else:
            batch_inds = latent["batch_index"] if "batch_index" in latent else None
            noise = comfy.sample.prepare_noise(latent_image, seed, batch_inds)

        noise_mask = None
        if "noise_mask" in latent:
            noise_mask = latent["noise_mask"]

        preview_format = "JPEG"
        if preview_format not in ["JPEG", "PNG"]:
            preview_format = "JPEG"

        previewer = False

        if preview_latent:
            previewer = latent_preview.get_previewer(device, model.model.latent_format)  

        pbar = comfy.utils.ProgressBar(steps)
        def callback(step, x0, x, total_steps):
            preview_bytes = None
            if previewer:
                preview_bytes = previewer.decode_latent_to_preview_image(preview_format, x0)
            pbar.update_absolute(step + 1, total_steps, preview_bytes)

        samples = comfy.sample.sample(model, noise, steps, cfg, sampler_name, scheduler, positive, negative, latent_image,
                                    denoise=denoise, disable_noise=disable_noise, start_step=start_step, last_step=last_step,
                                    force_full_denoise=force_full_denoise, noise_mask=noise_mask, callback=callback, disable_pbar=disable_pbar, seed=seed)
        
        out = latent.copy()
        out["samples"] = samples
        return out