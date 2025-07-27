from .src.lbt.image_loader import NODE_CLASS_MAPPINGS as image_loader_NCM
from .src.lbt.image_saver import NODE_CLASS_MAPPINGS as image_saver_NCM
from .src.lbt.folder_info import NODE_CLASS_MAPPINGS as folder_info_NCM
from .src.lbt.video_loader import NODE_CLASS_MAPPINGS as video_loader_NCM
from .src.lbt.text_loader import NODE_CLASS_MAPPINGS as text_loader_NCM
from .src.lbt.string_to_list import NODE_CLASS_MAPPINGS as string_to_list_NCM
from .src.lbt.list_info import NODE_CLASS_MAPPINGS as list_info_NCM
from .src.lbt.image_loader_from_list import NODE_CLASS_MAPPINGS as image_loader_from_list_NCM
from .src.lbt.image_combiner import NODE_CLASS_MAPPINGS as image_combiner_NCM
from .src.lbt.crop_by_mask import NODE_CLASS_MAPPINGS as crop_by_mask_NCM
from .src.lbt.combine_from_list import NODE_CLASS_MAPPINGS as combine_from_list_NCM
from .src.lbt.text_image_comparison import NODE_CLASS_MAPPINGS as text_image_comparison_NCM

NODE_CLASS_MAPPINGS = {
    **image_loader_NCM,
    **image_saver_NCM,
    **folder_info_NCM,
    **video_loader_NCM,
    **text_loader_NCM,
    **string_to_list_NCM,
    **list_info_NCM,
    **image_loader_from_list_NCM,
    **image_combiner_NCM,
    **crop_by_mask_NCM,
    **combine_from_list_NCM,
    **text_image_comparison_NCM,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_LoadImagesFromFolder": "Load Image From Folder (LBT)",
    "LBT_SaveImage": "Save Image (LBT)",
    "LBT_GetFolderInfo": "Get Folder Info (LBT)",
    "LBT_LoadVideoFromFolder": "Load Video From Folder (LBT)",
    "LBT_LoadTextFromFolder": "Load Text From Folder (LBT)",
    "LBT_StringToList": "Convert String to List (LBT)",
    "LBT_ListInfo": "Get List Info (LBT)",
    "LBT_LoadImagesFromList": "Load Images From List (LBT)",
    "LBT_CombineImagesFromBatch": "Combine Images From Batch (LBT)",
    "LBT_CropByMask": "Crop Image by Mask (LBT)",
    "LBT_CombineImagesFromList": "Combine Images From List (LBT)",
    "LBT_TextImageLibraryComparison": "Text Image Library Comparison (LBT)",
}
