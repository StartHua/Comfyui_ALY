# Comfyui-Mine

自定义 Comfyui 节点

1.CXH_GPT 节点 安装参考：https://www.bilibili.com/video/BV1A94y1A7Mr/

报错：ModuleNotFoundError: No module named 'gptcpp_node' 注意需要看视频结尾其实是需要comfyui_nodes节点，如果不需要GPT节点可以删除CXH_GPT.py，也到__init__.py把CXH_GPT删除

2.CXH_IMAGE 节点 接受一个图片路径输出图片

3.CXH_ALY_Seg_Cloth 接入阿里云的图片切割
(1).需要登录阿里云https://help.aliyun.com/zh/viapi/developer-reference/api-clothing-segmentation?spm=a2c4g.11186623.0.0.2b14193eJd1HnE
获取 key 填写到 AssetKey.json

(2).需要安装依赖：requirements.txt
python_embeded\python.exe pip  install -r requirements.txt

如果阿里的库安装不上可以到群里获取库直接解压。

链接：https://pan.baidu.com/s/1Wt7fLMktnlwuDCrGeV7DqQ 
提取码：9c0f

![2da457a1d6d40ca81435c71f7f9a13f](https://github.com/StartHua/Comfyui-Mine/assets/22284244/39173f9d-629c-4766-a852-efb358c45d48)
