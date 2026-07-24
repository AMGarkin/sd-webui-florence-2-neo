# sd-webui-florence-2

[English](README.md) **|** [中文](README_JP.md)

**sd-webui-florence-2** can identify the content of images and describe them in natural language.

## Changes from the original version

Modified for use with [SD WebUI Forge Neo](https://github.com/Haoming02/sd-webui-forge-classic)  
Modifications based on [ComfyUI-Florence2 v1.0.7](https://github.com/kijai/ComfyUI-Florence2/tree/6c766b13f4908a86cfbd6357d6d485c80e0f3a2f)

Note: You can change default values selected on the Florence 2 tab in the ui-config.json file located in the root directory of WebUI Forge Neo.

```text
    "florence/Select Model/visible": true,
    "florence/Select Model/value": "MiaoshouAI/Florence-2-large-PromptGen-v2.0",
    "florence/Max new token/visible": true,
    "florence/Max new token/value": 1024,
    "florence/Prompt Type/visible": true,
    "florence/Prompt Type/value": "<MORE_DETAILED_CAPTION>",
    "florence/Generate/visible": true,
    "florence/Send to txt2img/visible": true,
    "florence/Send to img2img/visible": true
```

## Installation

> video: [https://www.bilibili.com/video/BV1JV8fePE6M/](https://www.bilibili.com/video/BV1JV8fePE6M/)

1. Extensions -> Install from URL -> Enter URL of this repository -> Press Install button or clone this repository under extensions/

```bash
git clone https://github.com/ilyq/sd-webui-florence-2 extensions/sd-webui-florence-2
```

## Important Notice

1. transformers version

   1.1. Old versions of transformers do not support Florence-2, and using them will result in the following error:

   ```text
   TypeError: Object of type Florence2LanguageConfig is not JSON serializable
   ```

   1.2. Automatic1111's Web UI specifies an older version of transformers, 4.30.2, in the requirements.txt and requirements_versions.txt files.  
   1.3. Updating the Transformers version may trigger other errors; please test it yourself.

2. model path: `models/LLM`

## Screenshot

![](screenshot.jpg)

## Reference

[https://huggingface.co/microsoft/Florence-2-large](https://huggingface.co/microsoft/Florence-2-large)

## Some of the Florence-2 models on Hugging Face

[MiaoshouAI/Florence-2-large-PromptGen-v2.0](https://huggingface.co/MiaoshouAI/Florence-2-large-PromptGen-v2.0) - recommended  
[MiaoshouAI/Florence-2-base-PromptGen-v2.0](https://huggingface.co/MiaoshouAI/Florence-2-base-PromptGen-v2.0) - recommended  
[gokaygokay/Florence-2-Flux-Large](https://huggingface.co/gokaygokay/Florence-2-Flux-Large)  
[thwri/CogFlorence-2.2-Large](https://huggingface.co/thwri/CogFlorence-2.2-Large)  
[ljnlonoljpiljm/florence-2-large-nsfw-pretrain](https://huggingface.co/ljnlonoljpiljm/florence-2-large-nsfw-pretrain)  
[microsoft/Florence-2-large-ft](https://huggingface.co/microsoft/Florence-2-large-ft)  
[microsoft/Florence-2-base-ft](https://huggingface.co/microsoft/Florence-2-base-ft)  
