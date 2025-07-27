# LBT ComfyUI Custom Nodes

This repository contains a collection of custom nodes for ComfyUI, designed to enhance image and video processing workflows.

## Installation

Follow these steps to install the custom nodes and their dependencies.

### 1. Place the Custom Nodes

Navigate to your ComfyUI installation directory. Locate the `custom_nodes` folder.
Place the entire `Comfyui_LBT` folder (which contains this README) into the `ComfyUI/custom_nodes/` directory.

Your directory structure should look like this:

```
ComfyUI/
└── custom_nodes/
    └── Comfyui_LBT/
        ├── __init__.py
        ├── requirements.txt
        └── src/
            └── lbt/
                ├── folder_info.py
                ├── image_loader.py
                ├── image_saver.py
                ├── text_loader.py
                └── video_loader.py
```

### 2. Install Dependencies

These custom nodes require additional Python libraries.

Open a command prompt or terminal. Navigate to the root directory of your ComfyUI installation (where `main.py` is located).

Ensure you are in the Python environment used by your ComfyUI installation. This might involve activating a virtual environment or simply running `python` from the correct directory. If you are unsure how to do this, please refer to your ComfyUI installation guide.

Once your environment is activated, install the required packages using `pip`:

```bash
pip install -r custom_nodes/Comfyui_LBT/requirements.txt
```

### 3. Restart ComfyUI

After installing the dependencies, you **must** restart your ComfyUI application for the new nodes to appear and function correctly.

## Node List


### 1. Load Image From Folder (LBT)


- **Description:** Loads a single image from a specified folder based on an index (seed). Useful for processing images one by one from a directory.
- **Inputs:**
    - `folder_path` (STRING): The absolute path to the folder containing images.
    - `seed` (INT): An integer that determines which image to load. This input is set to `Increment` by default, meaning it will automatically load the next image in the folder with each workflow execution.
- **Outputs:**
    - `image` (IMAGE): The loaded image.
    - `full_filename` (STRING): The full filename of the loaded image (e.g., `image001.png`).
    - `filename_no_ext` (STRING): The filename without the extension (e.g., `image001`).

### 2. Save Image (LBT)


- **Description:** Saves an image to a specified path with flexible naming options.
- **Inputs:**
    - `images` (IMAGE): The image(s) to save.
    - `filename_text` (STRING): The base filename or full path depending on the `mode`.
    - `save_path` (STRING): The directory where the image will be saved.
    - `mode` (ENUM: `Relative`, `Absolute`):
        - `Relative`: Uses `filename_text` as the base name and appends the chosen `format` extension.
        - `Absolute`: Uses `filename_text` as the full filename (including extension) and automatically detects the save format from it. `save_path` is still used as the base directory.
    - `format` (OPTIONAL ENUM: `png`, `jpg`, `jpeg`, `bmp`, `webp`): The image format to save as. Only used in `Relative` mode.
- **Behavior:** If a file with the same name already exists at the target path, the node will raise an error to prevent overwriting.

### 3. Get Folder Info (LBT)


- **Description:** Scans a specified folder and outputs the count of images, videos, and text files.
- **Inputs:**
    - `folder_path` (STRING): The absolute path to the folder to scan.
- **Outputs:**
    - `image_count` (INT): Number of image files found.
    - `video_count` (INT): Number of video files found.
    - `txt_count` (INT): Number of text files found.
- **Note:** To see the output, you need to connect these outputs to a display node (e.g., a `Primitive` node or a `Show Text` node from another custom node pack) and run the workflow once.

### 4. Load Video From Folder (LBT)


- **Description:** Loads the first frame of a video from a specified folder based on an index (seed).
- **Inputs:**
    - `folder_path` (STRING): The absolute path to the folder containing video files.
    - `seed` (INT): An integer that determines which video to load. This input is set to `Increment` by default, meaning it will automatically load the next video's first frame in the folder with each workflow execution.
- **Outputs:**
    - `image` (IMAGE): The first frame of the loaded video as an image.
    - `full_filename` (STRING): The full filename of the loaded video (e.g., `video001.mp4`).
    - `filename_no_ext` (STRING): The filename without the extension (e.g., `video001`).
    - `audio` (AUDIO): A placeholder for audio data (currently empty).
    - `video_info` (VHS_VIDEOINFO): A placeholder for video metadata (currently empty).

### 5. Load Text From Folder (LBT)

- **Description:** Loads a single text file (`.txt`) from a specified folder based on an index (seed).
- **Inputs:**
    - `folder_path` (STRING): The absolute path to the folder containing text files.
    - `seed` (INT): An integer that determines which text file to load. This input is set to `Increment` by default, meaning it will automatically load the next file in the folder with each workflow execution.
- **Outputs:**
    - `text` (STRING): The content of the loaded text file.
    - `full_filename` (STRING): The full filename of the loaded text file (e.g., `document.txt`).
    - `filename_no_ext` (STRING): The filename without the extension (e.g., `document`).

### 6. Load Images From List (LBT)

- **Description:** Loads multiple images from a folder based on a provided list of filenames (without extension). It can automatically resize images to match the first loaded image's dimensions.
- **Inputs:**
    - `lbt_list` (LBT_LIST): A list of filenames (e.g., from `Convert String to List`) to load.
    - `folder_path` (STRING): The absolute path to the folder containing the images.
    - `resize_mode` (ENUM: `Pad`, `Crop`, `Stretch`, `None`): Method to handle images with different dimensions.
        - `Pad`: Resizes while maintaining aspect ratio and fills empty space with black.
        - `Crop`: Resizes and crops the image to fit the target dimensions.
        - `Stretch`: Stretches the image to the target dimensions, ignoring aspect ratio.
        - `None`: Skips images with different dimensions.
- **Outputs:**
    - `image` (IMAGE): A batch of loaded and processed images.

### 7. Crop Image by Mask (LBT)

- **Description:** Crops an image to the bounding box of its mask. It can use an external mask or the image's own alpha channel.
- **Inputs:**
    - `image` (IMAGE): The image to be cropped.
    - `offset` (INT): An integer to expand (positive value) or shrink (negative value) the crop area around the mask.
    - `mask` (OPTIONAL MASK): An external mask to define the crop area. If not provided, the node uses the image's alpha channel.
- **Outputs:**
    - `image` (IMAGE LIST): A list of cropped images. The output is a list because each image in a batch can be cropped to a different size.
- **Behavior:** If an external mask is provided, its dimensions must match the image's dimensions, otherwise, the node will raise an error.

### 8. Combine Images From Batch (LBT)

- **Description:** Combines a batch of **identically-sized** images into a single large image.
- **Inputs:**
    - `images` (IMAGE): A batch of images. All images must have the same dimensions.
    - `direction` (ENUM: `horizontal`, `vertical`, `most_compact`): The layout direction.
    - `resize_mode` (ENUM: `Pad`, `Stretch`, `None`): Method to unify image sizes before combining. `Pad` is recommended.
    - `spacing` (INT): The number of pixels to add as a gap between images.
    - `keep_alpha` (BOOLEAN): If checked, preserves transparency and outputs an RGBA image. If unchecked, the image is flattened onto a solid background.
    - `bg_color` (STRING): A hex color code (e.g., `#000000`) for the background. Only active when `keep_alpha` is unchecked.
- **Outputs:**
    - `image` (IMAGE): The final combined image.

### 9. Combine Images From List (LBT)

- **Description:** A powerful node that arranges a list of **differently-sized** images (e.g., from `Crop Image by Mask`) into a single composite image.
- **Inputs:**
    - `images` (IMAGE LIST): A list of images to combine.
    - `direction` (ENUM: `horizontal`, `vertical`, `most_compact`): The layout direction.
    - `spacing` (INT): The number of pixels to add as a gap between images.
    - `alignment` (ENUM: `center`, `start`, `end`): How to align images within the layout when their sizes differ.
    - `keep_alpha` (BOOLEAN): If checked, preserves transparency and outputs an RGBA image. If unchecked, the image is flattened onto a solid background.
    - `bg_color` (STRING): A hex color code (e.g., `#000000`) for the background. Only active when `keep_alpha` is unchecked.
- **Outputs:**
    - `image` (IMAGE): The final combined image.

### 10. Text Image Library Comparison (LBT)

- **Description:** Scans a body of text to find mentions of image filenames from a specified folder. It then outputs a list of the unique filenames found, perfect for dynamically loading images based on a script or story.
- **Inputs:**
    - `text` (STRING): The text to analyze.
    - `folder_path` (STRING): The path to the folder containing your image library.
- **Outputs:**
    - `lbt_list` (LBT_LIST): A list of unique image filenames (without extension) that were mentioned in the text.
    - `unique_found_count` (INT): The count of unique images found.
    - `total_mentions` (INT): The total number of times any image from the library was mentioned in the text.
- **Behavior:** The search is case-insensitive and matches whole words only.


## Troubleshooting

- **Nodes not appearing:** Ensure the `1_Comfyui_LBT` folder is directly inside `ComfyUI/custom_nodes/` and you have restarted ComfyUI.
- **`ModuleNotFoundError` or `AttributeError`:** Make sure all dependencies are installed by running `pip install -r custom_nodes/1_Comfyui_LBT/requirements.txt` in your ComfyUI Python environment.
- **`KeyError: 'JPG'`:** This has been addressed in the latest version of `Save Image (LBT)`. Ensure your `requirements.txt` is up to date and you have restarted ComfyUI.
- **`Permission denied` errors:** Check if ComfyUI has the necessary read/write permissions for the specified `folder_path` or `save_path`.
- **Video loading issues:** Ensure `ffmpeg` is correctly installed and accessible by `comfyui-videohelpersuite` (which our video node relies on). Refer to `comfyui-videohelpersuite`'s documentation for `ffmpeg` setup.

If you encounter any other issues, please provide the full error message and steps to reproduce.
