from fastapi import APIRouter, Request
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import torch
import base64
from peft import PeftModel
from io import BytesIO
from rembg import remove
from PIL import Image

import asyncio

router = APIRouter(prefix='/robot', tags=['Robot'])

device = "cuda" if torch.cuda.is_available() else "cpu"

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
).to(device)

pipe.unet = PeftModel.from_pretrained(
    pipe.unet,
    "./app/ai/lora"
)

pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
semaphore = asyncio.Semaphore(1)


def run_pipe(prompt):
    with torch.no_grad():
        return pipe(prompt).images[0]

@router.post("/generate")
async def generate_image(request: Request) -> dict:
    data = await request.json()

    prompt = data.get("prompt")
    if not prompt:
        return {"error": "No prompt provided"}
    
    mode = data.get("mode")
    if mode == "background":
        prompt += ", wide landscape, 16:9"
    elif mode == "character":
        prompt += ", character, full body"

    async with semaphore:
        image = await asyncio.to_thread(run_pipe, prompt)

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return {
        "image": base64.b64encode(buffer.getvalue()).decode()
    }


def run_remove(input_image):
    return remove(input_image)

@router.post("/remove-bg")
async def remove_bg(request: Request):
    data = await request.json()

    image_base64 = data.get("image")
    if not image_base64:
        return {"error": "No image provided"}

    image_bytes = base64.b64decode(image_base64)

    input_image = Image.open(BytesIO(image_bytes)).convert("RGBA")

    output = await asyncio.to_thread(run_remove, input_image)

    buffer = BytesIO()
    output.save(buffer, format="PNG")

    return {
        "image": base64.b64encode(buffer.getvalue()).decode()
    }