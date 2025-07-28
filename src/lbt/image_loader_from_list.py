import os
import torch
import numpy as np
from PIL import Image

class LBT_LoadImagesFromList:
    """
    A node that loads images from a folder based on a list of filenames,
    with an option to resize them to match the first image's dimensions.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "lbt_list": ("LBTlist",),
                "folder_path": ("STRING", {"default": "E:\\ComfyUI\\input"}),
                "resize_mode": (["Pad", "Crop", "Stretch", "None"],),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "load_images"
    CATEGORY = "LBT"

    def resize_image(self, img, target_width, target_height, mode='Pad'):
        pil_img = Image.fromarray((img.squeeze(0).numpy() * 255).astype(np.uint8))
        original_width, original_height = pil_img.size

        if mode == 'Stretch':
            resized_img = pil_img.resize((target_width, target_height), Image.LANCZOS)
        elif mode == 'Pad' or mode == 'Crop':
            ratio = min(target_width / original_width, target_height / original_height)
            if mode == 'Crop':
                ratio = max(target_width / original_width, target_height / original_height)
            
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            
            resized_img = pil_img.resize((new_width, new_height), Image.LANCZOS)
            
            final_img = Image.new("RGB", (target_width, target_height), (0, 0, 0))
            left = (target_width - new_width) // 2
            top = (target_height - new_height) // 2
            final_img.paste(resized_img, (left, top))
            
            if mode == 'Crop':
                crop_left = (new_width - target_width) // 2
                crop_top = (new_height - target_height) // 2
                crop_right = crop_left + target_width
                crop_bottom = crop_top + target_height
                final_img = final_img.crop((crop_left, crop_top, crop_right, crop_bottom))

            resized_img = final_img
        else: # Should not happen if validation is correct
            return img

        return torch.from_numpy(np.array(resized_img).astype(np.float32) / 255.0)[None,]

    def load_images(self, lbt_list, folder_path, resize_mode):
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.webp']
        images = []
        target_size = None

        for item in lbt_list:
            found = False
            for ext in valid_extensions:
                file_path = os.path.join(folder_path, f"{item}{ext}")
                if os.path.exists(file_path):
                    i = Image.open(file_path).convert("RGB")
                    image = np.array(i).astype(np.float32) / 255.0
                    image = torch.from_numpy(image)[None,]

                    if target_size is None:
                        target_size = (image.shape[2], image.shape[1])  # (width, height)
                    
                    if (image.shape[2], image.shape[1]) != target_size:
                        if resize_mode != "None":
                            image = self.resize_image(image, target_size[0], target_size[1], resize_mode)
                        else:
                            print(f"Warning: Image '{item}{ext}' has different dimensions and will be skipped.")
                            continue

                    images.append(image)
                    found = True
                    break
            if not found:
                print(f"Warning: Image '{item}' not found in folder '{folder_path}'")

        if not images:
            return (torch.empty(0),)

        return (torch.cat(images, dim=0),)

NODE_CLASS_MAPPINGS = {
    "LBT_LoadImagesFromList": LBT_LoadImagesFromList
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_LoadImagesFromList": "Load Images From List (LBT)"
}
