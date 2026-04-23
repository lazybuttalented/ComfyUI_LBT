import os
import torch
import numpy as np
from PIL import Image


class LBT_LoadImageFromPath:
    """
    Loads an image from a given file path.
    - If the file exists, returns the image and True.
    - If the file does not exist, returns a 100x100 white image and False.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "file_path": ("STRING", {"default": "C:/path/to/image.png", "multiline": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN")
    RETURN_NAMES = ("image", "file_exists")
    FUNCTION = "load_image"
    CATEGORY = "LBT"

    @classmethod
    def IS_CHANGED(cls, file_path):
        # Always re-check file existence on each run
        if os.path.isfile(file_path):
            return os.path.getmtime(file_path)
        return float("nan")

    def load_image(self, file_path):
        if os.path.isfile(file_path):
            try:
                pil_image = Image.open(file_path).convert("RGB")
                image_np = np.array(pil_image).astype(np.float32) / 255.0
                image_tensor = torch.from_numpy(image_np)[None,]
                return (image_tensor, True)
            except Exception as e:
                print(f"LBT_LoadImageFromPath Error: Failed to load image '{file_path}'. Error: {e}")
                # Fall through to return white image + False

        # File not found or failed to load — return 100x100 white image
        white_np = np.ones((100, 100, 3), dtype=np.float32)
        white_tensor = torch.from_numpy(white_np)[None,]
        return (white_tensor, False)


NODE_CLASS_MAPPINGS = {
    "LBT_LoadImageFromPath": LBT_LoadImageFromPath,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_LoadImageFromPath": "Load Image from Path (LBT)",
}
