import os
import sys

# Ensure extension root is in sys.path
scripts_dir = os.path.dirname(os.path.abspath(__file__))
ext_root = os.path.dirname(scripts_dir)
if ext_root not in sys.path:
    sys.path.append(ext_root)

import inspect
from unittest.mock import patch

import torch
import gradio as gr
from PIL import Image

import transformers
from transformers.dynamic_module_utils import get_imports
from transformers import AutoProcessor, AutoModelForCausalLM

from modules import devices
from modules.paths_internal import models_path
import modules.infotext_utils as parameters_copypaste

try:
    from modules.call_queue import wrap_gradio_gpu_call
except ImportError:
    from webui import wrap_gradio_gpu_call  # pylint: disable=import-error


# https://huggingface.co/microsoft/Florence-2-large/blob/main/sample_inference.ipynb & finetune models dscriptions
available_prompt_type = [
    # -- basics (Microsoft) --
    "<MORE_DETAILED_CAPTION>",
    "<DETAILED_CAPTION>",
    "<CAPTION>",
    # "<OD>",                               # object detection
    # "<DENSE_REGION_CAPTION>",
    # "<REGION_PROPOSAL>",
    # "<CAPTION_TO_PHRASE_GROUNDING>",      # this needs additional text input
    # "<REFERRING_EXPRESSION_SEGMENTATION>",
    # "<REGION_TO_SEGMENTATION>",
    # "<OPEN_VOCABULARY_DETECTION>",
    # "<REGION_TO_CATEGORY>",
    # "<REGION_TO_DESCRIPTION>",
    "<OCR>",
    # "<OCR_WITH_REGION>",
    # -- gokay aydogan --
    "<DESCRIPTION>",                        # Flux-Large, generates tags. PromptGen-v2.0 works too.
    # -- MiaoshouAI --
    "<GENERATE_TAGS>",
    "<MIXED_CAPTION>",
    "<MIXED_CAPTION_PLUS>",                 # PromptGen-v2.0
    "<ANALYZE>",                            # PromptGen-v2.0
    # -- HuggingFaceM4 --
    # "<DocVQA>",                           # use: "<DocVQA>" + question
]

available_models = [
    "MiaoshouAI/Florence-2-large-PromptGen-v2.0",
    "MiaoshouAI/Florence-2-base-PromptGen-v2.0",
    # "MiaoshouAI/Florence-2-large-PromptGen-v1.5",
    # "MiaoshouAI/Florence-2-base-PromptGen-v1.5",
    "gokaygokay/Florence-2-Flux-Large",
    #"gokaygokay/Florence-2-SD3-Captioner",
    "thwri/CogFlorence-2.2-Large",
    # "thwri/CogFlorence-2.1-Large",
    # "HuggingFaceM4/Florence-2-DocVQA",
    "ljnlonoljpiljm/florence-2-large-nsfw-pretrain",
    "microsoft/Florence-2-large-ft",
    "microsoft/Florence-2-base-ft",
    # "microsoft/Florence-2-large",
    # "microsoft/Florence-2-base",
]


def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    try:
        if not str(filename).endswith("modeling_florence2.py"):
            return get_imports(filename)
        imports = get_imports(filename)
        imports.remove("flash_attn")
    except:
        print(f"No flash_attn import to remove")
        pass
    return imports


def generate_prompt_fn(
    image: Image,
    model_name: str,
    max_new_token: float,
    prompt_type: str,
):

    model_path = os.path.join(models_path, "LLM", model_name)

    if not os.path.exists(model_path):
        print(f"Downloading model to: {model_path}")
        from huggingface_hub import snapshot_download

        snapshot_download(
            repo_id=model_name, local_dir=model_path, local_dir_use_symlinks=False
        )

    if transformers.__version__ < '4.51.0':
        with patch("transformers.dynamic_module_utils.get_imports", fixed_get_imports): #workaround for unnecessary flash_attn requirement
             model = AutoModelForCausalLM.from_pretrained(model_path, attn_implementation="eager", torch_dtype=torch.float32, trust_remote_code=True).to(devices.device)
    else:
        from Florence2.modeling_florence2 import Florence2ForConditionalGeneration
        model = Florence2ForConditionalGeneration.from_pretrained(model_path, attn_implementation="eager", dtype=torch.float32, local_files_only=True).to(devices.device)
    processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True, local_files_only=True)

    inputs = processor(text=prompt_type, images=image, return_tensors="pt", do_rescale=False).to(devices.device)

    with torch.no_grad():
        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=int(max_new_token),
            do_sample=False,
            num_beams=3,
            use_cache=False,
        )

    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

    parsed_answer = processor.post_process_generation(
        generated_text,
        task=prompt_type,
        image_size=(image.width, image.height),
    )
    print(parsed_answer)

    result = parsed_answer[prompt_type]

    model.to(devices.cpu)

    return result, result


def on_ui_tabs():

    with gr.Blocks(analytics_enabled=False) as florence_interface:
        with gr.Row():
            # input
            with gr.Column(variant="panel"):
                if "sources" in inspect.signature(gr.Image).parameters:
                    image = gr.Image(sources=["upload"], interactive=True, type="pil")
                else:
                    image = gr.Image(interactive=True, type="pil")

                model_name = gr.Dropdown(
                    label="Select Model",
                    choices=available_models,
                    value=available_models[0],
                )

                with gr.Row():
                    max_new_token = gr.Number(
                        label="Max new token", value=1024, minimum=1, maximum=4096
                    )
                    prompt_type = gr.Dropdown(
                        label="Prompt Type",
                        choices=available_prompt_type,
                        value=available_prompt_type[0],
                    )

                generate_btn = gr.Button(value="Generate", variant="primary")

            # output
            with gr.Column(variant="panel"):
                tags = gr.State(value="")
                html_tags = gr.HTML(
                    value="Output<br><br><br><br>",
                    label="Tags",
                    elem_id="tags",
                )

                with gr.Row():
                    buttons = parameters_copypaste.create_buttons(["txt2img", "img2img"])

                for tabname, button in buttons.items():
                    parameters_copypaste.register_paste_params_button(
                        parameters_copypaste.ParamBinding(
                            paste_button=button,
                            tabname=tabname,
                            source_text_component=tags,
                            source_image_component=None,
                        )
                    )

            generate_btn.click(
                fn=wrap_gradio_gpu_call(generate_prompt_fn),
                inputs=[image, model_name, max_new_token, prompt_type + " Describe this image in great detail." if prompt_type == "<DESCRIPTION>" else prompt_type],
                outputs=[tags, html_tags],
            )

    return [(florence_interface, "Florence 2", "florence")]


# Setup A1111 initialisation hooks
try:
    import modules.script_callbacks as script_callbacks

    script_callbacks.on_ui_tabs(on_ui_tabs)
except:
    pass
