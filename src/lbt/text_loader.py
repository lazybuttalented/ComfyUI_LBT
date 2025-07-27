import os

class LBT_LoadTextFromFolder:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "C:/path/to/text"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "step": 1, "control_after_generate": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("text", "full_filename", "filename_no_ext")
    FUNCTION = "load_text_by_index"
    CATEGORY = "LBT"

    def load_text_by_index(self, folder_path, seed):
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        valid_extensions = ['.txt']
        text_files = sorted([f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in valid_extensions])

        if not text_files:
            return ("", "", "")

        selected_index = seed % len(text_files)
        
        selected_filename = text_files[selected_index]
        txt_path = os.path.join(folder_path, selected_filename)

        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                text_content = file.read()
        except Exception as e:
            print(f"Error reading file {txt_path}: {e}")
            return ("", selected_filename, os.path.splitext(selected_filename)[0])

        full_filename = selected_filename
        filename_no_ext = os.path.splitext(selected_filename)[0]

        return (text_content, full_filename, filename_no_ext)

NODE_CLASS_MAPPINGS = {
    "LBT_LoadTextFromFolder": LBT_LoadTextFromFolder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_LoadTextFromFolder": "Load Text (LBT)",
}
