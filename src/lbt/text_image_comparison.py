import os
import re

class LBT_TextImageLibraryComparison:
    """
    A node that compares a body of text against a library of image filenames from a folder.
    It finds which unique images are mentioned and counts the total number of mentions.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "A text mentioning a cat, another cat, and a dog. The cat is cute."}),
                "folder_path": ("STRING", {"default": "E:\\ComfyUI\\input"}),
            },
        }

    RETURN_TYPES = ("LBT_LIST", "INT", "INT")
    RETURN_NAMES = ("lbt_list", "unique_found_count", "total_mentions")
    FUNCTION = "compare_text_to_library"
    CATEGORY = "LBT"

    def compare_text_to_library(self, text, folder_path):
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.webp']
        try:
            image_names = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in valid_extensions]
        except Exception as e:
            print(f"Error reading image library folder: {e}")
            return ([], 0, 0)

        if not image_names:
            return ([], 0, 0)

        found_unique_names = set()
        total_mentions_count = 0
        
        for name in image_names:
            try:
                # Use word boundaries to match whole words only
                pattern = r'\b' + re.escape(name) + r'\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                num_matches = len(matches)
                
                if num_matches > 0:
                    found_unique_names.add(name)
                    total_mentions_count += num_matches
            except re.error as e:
                print(f"Regex error for name '{name}': {e}")
                continue
        
        # Sort the list for deterministic output
        output_list = sorted(list(found_unique_names))
        unique_found_count = len(output_list)

        return (output_list, unique_found_count, total_mentions_count)

NODE_CLASS_MAPPINGS = {
    "LBT_TextImageLibraryComparison": LBT_TextImageLibraryComparison
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_TextImageLibraryComparison": "Text Image Library Comparison (LBT)"
}
