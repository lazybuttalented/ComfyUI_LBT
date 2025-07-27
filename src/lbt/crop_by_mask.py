import torch
import numpy as np
from PIL import Image

class LBT_CropByMask:
    """
    A node to crop an image based on a provided mask or its own alpha channel.
    The crop is bound to the non-zero area of the mask.
    An offset can be provided to add padding or crop further into the mask.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "offset": ("INT", {"default": 0, "min": -8192, "max": 8192, "step": 1}),
            },
            "optional": {
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "crop_by_mask"
    CATEGORY = "LBT"

    def crop_by_mask(self, image: torch.Tensor, offset: int, mask: torch.Tensor = None):
        batch_size, img_h, img_w, img_c = image.shape
        
        if mask is not None:
            if mask.shape[1] != img_h or mask.shape[2] != img_w:
                raise ValueError(f"Mask dimensions ({mask.shape[1]}x{mask.shape[2]}) do not match image dimensions ({img_h}x{img_w}).")
        elif img_c != 4:
            print("Warning: LBT_CropByMask requires an external mask or an image with an alpha channel. Returning original image.")
            return ([image[i].unsqueeze(0) for i in range(batch_size)],)

        cropped_images = []
        for i in range(batch_size):
            single_image_tensor = image[i]
            pil_image = Image.fromarray((single_image_tensor.numpy() * 255).astype(np.uint8))

            if mask is not None:
                mask_tensor = mask[i]
                pil_mask = Image.fromarray((mask_tensor.numpy() * 255).astype(np.uint8), 'L')
            else: # Use alpha channel
                pil_mask = pil_image.getchannel('A')

            bbox = pil_mask.getbbox()

            if bbox is None:
                cropped_images.append(torch.zeros((1, 1, 1, img_c))) # Return a tiny tensor
                continue

            # Apply offset
            left, top, right, bottom = bbox
            left -= offset
            top -= offset
            right += offset
            bottom += offset

            # Clamp to image boundaries
            left = max(0, left)
            top = max(0, top)
            right = min(pil_image.width, right)
            bottom = min(pil_image.height, bottom)

            if left >= right or top >= bottom:
                cropped_images.append(torch.zeros((1, 1, 1, img_c)))
                continue

            cropped_pil = pil_image.crop((left, top, right, bottom))
            
            cropped_np = np.array(cropped_pil).astype(np.float32) / 255.0
            cropped_tensor = torch.from_numpy(cropped_np).unsqueeze(0)
            cropped_images.append(cropped_tensor)

        return (cropped_images,)

NODE_CLASS_MAPPINGS = {
    "LBT_CropByMask": LBT_CropByMask
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_CropByMask": "Crop Image by Mask (LBT)"
}
