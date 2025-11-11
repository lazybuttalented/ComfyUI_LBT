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
                "image_sequence": ("BOOLEAN", {"default": True}),
                "overwrite": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "format": (["png", "jpg", "jpeg", "bmp", "webp"],),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "LBT"

    def save_images(self, images, filename_text, save_path, mode, image_sequence, overwrite=False, format="png"):
        if not os.path.isdir(save_path):
            os.makedirs(save_path, exist_ok=True)

        # Map common extensions to Pillow's internal format names
        format_map = {
            "jpg": "JPEG",
            "jpeg": "JPEG",
            "png": "PNG",
            "bmp": "BMP",
            "webp": "WEBP",
        }

        images_to_save = images if image_sequence else images[0:1]

        for i, image in enumerate(images_to_save):
            image = image.cpu().numpy()
            image = (image * 255).astype(np.uint8)
            pil_image = Image.fromarray(image)

            if mode == 'Relative':
                filenames = filename_text.split('\n') if '\n' in filename_text else [filename_text]
                base_filename = filenames[i % len(filenames)]

                if image_sequence and len(images_to_save) > 1:
                    final_filename = f"{base_filename}_{i:04d}"
                else:
                    final_filename = base_filename
                
                file_path = os.path.join(save_path, f"{final_filename}.{format}")
                save_format = format_map.get(format, format).upper()

            elif mode == 'Absolute':
                filenames = filename_text.split('\n') if '\n' in filename_text else [filename_text]
                current_full_filename = filenames[i % len(filenames)]
                
                if image_sequence and len(images_to_save) > 1:
                    name, ext = os.path.splitext(current_full_filename)
                    final_full_filename = f"{name}_{i:04d}{ext}"
                else:
                    final_full_filename = current_full_filename

                _, ext = os.path.splitext(final_full_filename)
                file_ext = ext[1:].lower() if ext else "png"
                save_format = format_map.get(file_ext, file_ext).upper()
                file_path = os.path.join(save_path, final_full_filename)
            
            if not overwrite and os.path.exists(file_path):
                # Find a new filename by appending a number
                counter = 1
                while os.path.exists(file_path):
                    if mode == 'Relative':
                        if image_sequence and len(images_to_save) > 1:
                            new_filename = f"{base_filename}_{i:04d}_{counter}"
                        else:
                            new_filename = f"{base_filename}_{counter}"
                        file_path = os.path.join(save_path, f"{new_filename}.{format}")
                    elif mode == 'Absolute':
                        name, ext = os.path.splitext(current_full_filename)
                        if image_sequence and len(images_to_save) > 1:
                            new_filename = f"{name}_{i:04d}_{counter}{ext}"
                        else:
                            new_filename = f"{name}_{counter}{ext}"
                        file_path = os.path.join(save_path, new_filename)
                    counter += 1

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
