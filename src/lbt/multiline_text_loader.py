import os

try:
    import folder_paths
except ImportError:
    folder_paths = None

class LBT_LoadMultilineText:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory() if folder_paths else "input"
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and f.lower().endswith('.txt')]
        return {
            "required": {
                "file": (sorted(files),),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "STRING", "STRING")
    RETURN_NAMES = ("prompt_batch", "count", "full_filename", "filename_no_ext")
    FUNCTION = "load_multiline_text"
    CATEGORY = "LBT"

    def load_multiline_text(self, file):
        input_dir = folder_paths.get_input_directory() if folder_paths else "input"
        txt_path = os.path.join(input_dir, file)

        if not os.path.isfile(txt_path):
            raise FileNotFoundError(f"File not found: {txt_path}")

        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except Exception as e:
            print(f"Error reading file {txt_path}: {e}")
            return ("", 0, file, os.path.splitext(file)[0])

        # Split by empty lines to get prompts
        prompts = [p.strip() for p in text_content.split('\n\n') if p.strip()]
        count = len(prompts)

        # Convert prompts list to batch format (newline separated)
        prompt_batch = '\n'.join(prompts)

        full_filename = file
        filename_no_ext = os.path.splitext(file)[0]

        return (prompt_batch, count, full_filename, filename_no_ext)

    @classmethod
    def VALIDATE_INPUTS(s, file):
        input_dir = folder_paths.get_input_directory() if folder_paths else "input"
        txt_path = os.path.join(input_dir, file)
        if not os.path.isfile(txt_path):
            return f"Invalid text file: {file}"
        return True

NODE_CLASS_MAPPINGS = {
    "LBT_LoadMultilineText": LBT_LoadMultilineText,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_LoadMultilineText": "Load Multiline Text (LBT)",
}
