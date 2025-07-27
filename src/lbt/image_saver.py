import os
import torch
import numpy as np
from PIL import Image
import folder_paths

class LBT_SaveImage:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                "filename_text": ("STRING", {"multiline": False, "default": "image_01"}),
                "save_path": ("STRING", {"default": folder_paths.get_output_directory()}),
                "mode": (["Relative", "Absolute"],),
            },
            "optional": {
                "format": (["png", "jpg", "jpeg", "bmp", "webp"],),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "LBT"

    def save_images(self, images, filename_text, save_path, mode, format="png"):
        if not os.path.isdir(save_path):
            os.makedirs(save_path, exist_ok=True)

        for i, image in enumerate(images):
            image = image.cpu().numpy()
            image = (image * 255).astype(np.uint8)
            pil_image = Image.fromarray(image)

            if mode == 'Relative':
                filenames = filename_text.split('\n') if '\n' in filename_text else [filename_text]
                current_filename = filenames[i % len(filenames)]
                
                file_path = os.path.join(save_path, f"{current_filename}.{format}")

            elif mode == 'Absolute':
                # In absolute mode, filename_text is expected to be the full filename with extension
                filenames = filename_text.split('\n') if '\n' in filename_text else [filename_text]
                current_full_filename = filenames[i % len(filenames)]
                
                # Extract extension from the filename_text
                _, ext = os.path.splitext(current_full_filename)
                # Remove the leading dot from the extension
                save_format = ext[1:].lower() if ext else "png" # Default to png if no extension
                
                # Map common extensions to Pillow's internal format names
                format_map = {
                    "jpg": "JPEG",
                    "jpeg": "JPEG",
                    "png": "PNG",
                    "bmp": "BMP",
                    "webp": "WEBP",
                }
                save_format = format_map.get(save_format, save_format).upper() # Ensure it's uppercase for Pillow

                file_path = os.path.join(save_path, current_full_filename)
            
            if os.path.exists(file_path):
                raise FileExistsError(f"File already exists, saving aborted: {file_path}")

            try:
                print(f"LBT_SaveImage: Attempting to save to: {file_path} with format: {save_format}")
                pil_image.save(file_path, format=save_format)
            except Exception as e:
                print(f"LBT_SaveImage Error: Failed to save image {file_path}. Error: {e}")
                import traceback
                traceback.print_exc()
                raise # Re-raise the exception to stop the workflow
            
        return {}

NODE_CLASS_MAPPINGS = {
    "LBT_SaveImage": LBT_SaveImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_SaveImage": "Save Image (LBT)",
}
