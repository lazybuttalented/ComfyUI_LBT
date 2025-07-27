import os
import torch
import numpy as np
from PIL import Image
import folder_paths

class LBT_LoadImagesFromFolder:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "C:/path/to/images"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "step": 1, "control_after_generate": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "full_filename", "filename_no_ext")
    FUNCTION = "load_image_by_index"
    CATEGORY = "LBT"

    def load_image_by_index(self, folder_path, seed):
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.webp']
        image_files = sorted([f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in valid_extensions])

        if not image_files:
            # Return empty tensors and strings if no images are found
            return (torch.empty(0), "", "")

        # Use modulo to loop the index
        selected_index = seed % len(image_files)
        
        selected_filename = image_files[selected_index]
        img_path = os.path.join(folder_path, selected_filename)

        # Load the single image
        i = Image.open(img_path)
        i = i.convert("RGB")
        image = np.array(i).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]

        # Get filename parts
        full_filename = selected_filename
        filename_no_ext = os.path.splitext(selected_filename)[0]

        return (image, full_filename, filename_no_ext)

NODE_CLASS_MAPPINGS = {
    "LBT_LoadImagesFromFolder": LBT_LoadImagesFromFolder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_LoadImagesFromFolder": "Load Images (LBT)",
}
