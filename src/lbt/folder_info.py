
import os

class LBT_GetFolderInfo:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "C:/path/to/folder"}),
            }
        }

    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("image_count", "video_count", "txt_count")
    FUNCTION = "get_counts"
    CATEGORY = "LBT"

    def get_counts(self, folder_path):
        if not os.path.isdir(folder_path):
            print(f"LBT_GetFolderInfo: Folder not found at {folder_path}")
            return (0, 0, 0)

        image_count = 0
        video_count = 0
        txt_count = 0

        image_exts = ['.png', '.jpg', '.jpeg', '.bmp', '.webp', '.gif']
        video_exts = ['.mp4', '.mov', '.avi', '.mkv', '.webm']

        try:
            for filename in os.listdir(folder_path):
                if os.path.isfile(os.path.join(folder_path, filename)):
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in image_exts:
                        image_count += 1
                    elif ext in video_exts:
                        video_count += 1
                    elif ext == '.txt':
                        txt_count += 1
        except Exception as e:
            print(f"LBT_GetFolderInfo: Error reading folder {folder_path}: {e}")
            return (0, 0, 0)

        return (image_count, video_count, txt_count)

NODE_CLASS_MAPPINGS = {
    "LBT_GetFolderInfo": LBT_GetFolderInfo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_GetFolderInfo": "Get Folder Info (LBT)",
}
