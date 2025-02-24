from diffusers import AutoPipelineForInpainting
from diffusers.utils import load_image
import torch

pipe = AutoPipelineForInpainting.from_pretrained("diffusers/stable-diffusion-xl-1.0-inpainting-0.1", torch_dtype=torch.float16, variant="fp16").to("cuda")

image = load_image("C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/face_with_eyebrows.jpg")
mask_image = load_image("C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/eyebrow_mask.png")




prompt = " soft angle eyebow and black color with natural and realistic eyebrows, high quality, photorealistic"
generator = torch.Generator(device="cuda").manual_seed(0)

image = pipe(
  prompt=prompt,
  image=image,
  mask_image=mask_image,
  guidance_scale=8.0,
  num_inference_steps=20,  # steps between 15 and 30 work well for us
  strength=0.99,  # make sure to use `strength` below 1.0
  generator=generator,
).images[0]

image.save("output.png")