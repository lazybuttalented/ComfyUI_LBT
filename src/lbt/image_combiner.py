import torch
import numpy as np
from PIL import Image, ImageOps
import math

class LBT_CombineImagesFromBatch:
    """
    A node to combine a list/batch of images into a single image using various layouts.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "direction": (["horizontal", "vertical", "most_compact"],),
                "resize_mode": (["Pad", "Stretch", "None"],),
                "spacing": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                "keep_alpha": ("BOOLEAN", {"default": True}),
                "bg_color": ("STRING", {"default": "#000000"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "combine_images"
    CATEGORY = "LBT"

    def combine_images(self, images, direction, resize_mode, spacing, keep_alpha, bg_color):
        if images is None or len(images) == 0:
            return (torch.empty(0),)

        pil_images = []
        for img_tensor in images:
            img_array = (img_tensor.numpy() * 255).astype(np.uint8)
            if img_tensor.shape[2] == 4 and keep_alpha:
                pil_images.append(Image.fromarray(img_array, 'RGBA'))
            else:
                pil_images.append(Image.fromarray(img_array, 'RGB'))

        # Determine target size for resizing
        max_width = max(img.width for img in pil_images)
        max_height = max(img.height for img in pil_images)

        if resize_mode != 'None':
            resized_pil_images = []
            for img in pil_images:
                if (img.width, img.height) == (max_width, max_height):
                    resized_pil_images.append(img)
                    continue

                if resize_mode == 'Stretch':
                    resized_img = img.resize((max_width, max_height), Image.LANCZOS)
                elif resize_mode == 'Pad':
                    pad_mode = 'RGBA' if keep_alpha else 'RGB'
                    pad_color = (0,0,0,0) if keep_alpha else bg_color
                    resized_img = Image.new(pad_mode, (max_width, max_height), pad_color)
                    img.thumbnail((max_width, max_height), Image.LANCZOS)
                    left = (max_width - img.width) // 2
                    top = (max_height - img.height) // 2
                    resized_img.paste(img, (left, top), img if img.mode=='RGBA' else None)
                
                resized_pil_images.append(resized_img)
            pil_images = resized_pil_images
        else:
            first_size = pil_images[0].size
            if not all(img.size == first_size for img in pil_images):
                raise ValueError("All images must have the same dimensions when resize_mode is 'None'.")

        canvas_mode = 'RGBA' if keep_alpha else 'RGB'
        canvas_color = (0,0,0,0) if keep_alpha else bg_color

        if direction == 'horizontal':
            total_width = sum(img.width for img in pil_images) + spacing * (len(pil_images) - 1)
            combined_image = Image.new(canvas_mode, (total_width, max_height), canvas_color)
            current_x = 0
            for img in pil_images:
                combined_image.paste(img, (current_x, 0), img if img.mode=='RGBA' else None)
                current_x += img.width + spacing
        elif direction == 'vertical':
            total_height = sum(img.height for img in pil_images) + spacing * (len(pil_images) - 1)
            combined_image = Image.new(canvas_mode, (max_width, total_height), canvas_color)
            current_y = 0
            for img in pil_images:
                combined_image.paste(img, (0, current_y), img if img.mode=='RGBA' else None)
                current_y += img.height + spacing
        elif direction == 'most_compact':
            num_images = len(pil_images)
            cols = math.ceil(math.sqrt(num_images))
            rows = math.ceil(num_images / cols)
            
            total_width = cols * max_width + spacing * (cols - 1)
            total_height = rows * max_height + spacing * (rows - 1)
            combined_image = Image.new(canvas_mode, (total_width, total_height), canvas_color)

            for i, img in enumerate(pil_images):
                row = i // cols
                col = i % cols
                x = col * (max_width + spacing)
                y = row * (max_height + spacing)
                combined_image.paste(img, (x, y), img if img.mode=='RGBA' else None)

        output_channels = 4 if keep_alpha else 3
        output_np = np.array(combined_image).astype(np.float32) / 255.0
        output_tensor = torch.from_numpy(output_np).unsqueeze(0)
        if output_tensor.shape[3] != output_channels:
             output_tensor = output_tensor[:,:,:,:output_channels]

        return (output_tensor,)

NODE_CLASS_MAPPINGS = {
    "LBT_CombineImagesFromBatch": LBT_CombineImagesFromBatch
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_CombineImagesFromBatch": "Combine Images From Batch (LBT)"
}