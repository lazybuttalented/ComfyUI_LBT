import torch
import numpy as np
from PIL import Image
import math

class LBT_CombineImagesFromList:
    """
    A node to arrange a list of differently-sized images into a single composite image.
    """
    INPUT_IS_LIST = True

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "direction": (["horizontal", "vertical", "most_compact"],),
                "spacing": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                "alignment": (["center", "start", "end"],),
                "keep_alpha": ("BOOLEAN", {"default": True}),
                "bg_color": ("STRING", {"default": "#000000"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "combine_images"
    CATEGORY = "LBT"

    def combine_images(self, images, direction, spacing, alignment, keep_alpha, bg_color):
        if isinstance(direction, list): direction = direction[0]
        if isinstance(alignment, list): alignment = alignment[0]
        if isinstance(spacing, list): spacing = spacing[0]
        if isinstance(keep_alpha, list): keep_alpha = keep_alpha[0]
        if isinstance(bg_color, list): bg_color = bg_color[0]

        if not images or not images[0].shape[0]:
            return (torch.empty(0),)

        pil_images = []
        for image_tensor in images:
            for i in range(image_tensor.shape[0]):
                single_tensor = image_tensor[i]
                img_array = (single_tensor.numpy() * 255).astype(np.uint8)
                if single_tensor.shape[2] == 4:
                    pil_images.append(Image.fromarray(img_array, 'RGBA'))
                else:
                    pil_images.append(Image.fromarray(img_array, 'RGB'))

        if not pil_images:
            return (torch.empty(0),)

        max_width = max(img.width for img in pil_images)
        max_height = max(img.height for img in pil_images)
        
        canvas = None
        canvas_mode = 'RGBA' if keep_alpha else 'RGB'
        canvas_color = (0,0,0,0) if keep_alpha else bg_color

        if direction == 'horizontal':
            total_width = sum(img.width for img in pil_images) + spacing * (len(pil_images) - 1)
            canvas = Image.new(canvas_mode, (total_width, max_height), canvas_color)
            current_x = 0
            for img in pil_images:
                y_pos = 0
                if alignment == 'center': y_pos = (max_height - img.height) // 2
                elif alignment == 'end': y_pos = max_height - img.height
                canvas.paste(img, (current_x, y_pos), img if img.mode == 'RGBA' else None)
                current_x += img.width + spacing

        elif direction == 'vertical':
            total_height = sum(img.height for img in pil_images) + spacing * (len(pil_images) - 1)
            canvas = Image.new(canvas_mode, (max_width, total_height), canvas_color)
            current_y = 0
            for img in pil_images:
                x_pos = 0
                if alignment == 'center': x_pos = (max_width - img.width) // 2
                elif alignment == 'end': x_pos = max_width - img.width
                canvas.paste(img, (x_pos, current_y), img if img.mode == 'RGBA' else None)
                current_y += img.height + spacing

        elif direction == 'most_compact':
            num_images = len(pil_images)
            cols = math.ceil(math.sqrt(num_images))
            rows = math.ceil(num_images / cols)
            
            cell_w, cell_h = max_width, max_height
            total_width = cols * cell_w + spacing * (cols - 1)
            total_height = rows * cell_h + spacing * (rows - 1)
            canvas = Image.new(canvas_mode, (total_width, total_height), canvas_color)

            for i, img in enumerate(pil_images):
                grid_row, grid_col = i // cols, i % cols
                cell_x, cell_y = grid_col * (cell_w + spacing), grid_row * (cell_h + spacing)

                inner_x, inner_y = 0, 0
                if alignment == 'center':
                    inner_x = (cell_w - img.width) // 2
                    inner_y = (cell_h - img.height) // 2
                elif alignment == 'end':
                    inner_x = cell_w - img.width
                    inner_y = cell_h - img.height

                canvas.paste(img, (cell_x + inner_x, cell_y + inner_y), img if img.mode == 'RGBA' else None)
        
        if canvas is None: raise ValueError(f"Unknown direction value: {direction}")

        if not keep_alpha:
            canvas = canvas.convert('RGB')

        output_np = np.array(canvas).astype(np.float32) / 255.0
        output_tensor = torch.from_numpy(output_np).unsqueeze(0)

        return (output_tensor,)

NODE_CLASS_MAPPINGS = {
    "LBT_CombineImagesFromList": LBT_CombineImagesFromList
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_CombineImagesFromList": "Combine Images From List (LBT)"
}
