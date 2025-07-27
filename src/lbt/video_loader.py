import os
import torch
import numpy as np
import cv2 # For video loading
import folder_paths

# Define video extensions based on comfyui-videohelpersuite
video_extensions = ['webm', 'mp4', 'mkv', 'gif', 'mov']

class LBT_LoadVideoFromFolder:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "C:/path/to/videos"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "step": 1, "control_after_generate": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "AUDIO", "VHS_VIDEOINFO")
    RETURN_NAMES = ("image", "full_filename", "filename_no_ext", "audio", "video_info")
    FUNCTION = "load_video_by_index"
    CATEGORY = "LBT"

    def load_video_by_index(self, folder_path, seed):
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        video_files = sorted([f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in video_extensions])

        if not video_files:
            # Return empty values if no videos are found
            # For AUDIO and VHS_VIDEOINFO, returning None might cause issues if downstream nodes expect specific types.
            # Providing minimal valid structures is safer.
            audio_output = {"waveform": torch.empty(0), "sample_rate": 0} # Minimal AUDIO structure
            video_info_output = {
                "source_fps": 0.0, "source_frame_count": 0, "source_duration": 0.0,
                "source_width": 0, "source_height": 0,
                "loaded_fps": 0.0, "loaded_frame_count": 0, "loaded_duration": 0.0,
                "loaded_width": 0, "loaded_height": 0,
            } # Minimal VHS_VIDEOINFO structure
            return (torch.empty(0), "", "", audio_output, video_info_output)

        selected_index = seed % len(video_files)
        selected_filename = video_files[selected_index]
        video_path = os.path.join(folder_path, selected_filename)

        # Load the first frame of the video using OpenCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"Could not open video file: {video_path}")

        ret, frame = cap.read()
        if not ret:
            cap.release()
            raise Exception(f"Could not read first frame from video: {video_path}")

        cap.release()

        # Convert frame from BGR to RGB and to ComfyUI's expected format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = np.array(frame).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,] # Add batch dimension

        full_filename = selected_filename
        filename_no_ext = os.path.splitext(selected_filename)[0]

        # Dummy outputs for audio and video_info to match VHS_LoadVideoPath
        # In a real scenario, you'd extract actual audio and video metadata here.
        audio_output = {"waveform": torch.empty(0), "sample_rate": 0} # Minimal AUDIO structure
        video_info_output = {
            "source_fps": 0.0, "source_frame_count": 0, "source_duration": 0.0,
            "source_width": 0, "source_height": 0,
            "loaded_fps": 0.0, "loaded_frame_count": 0, "loaded_duration": 0.0,
            "loaded_width": 0, "loaded_height": 0,
        } # Minimal VHS_VIDEOINFO structure

        return (image, full_filename, filename_no_ext, audio_output, video_info_output)

NODE_CLASS_MAPPINGS = {
    "LBT_LoadVideoFromFolder": LBT_LoadVideoFromFolder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_LoadVideoFromFolder": "Load Video From Folder (LBT)",
}
