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
    └── 1_Comfyui_LBT/          # or "Comfyui_LBT/" depending on install method
        ├── __init__.py
        ├── requirements.txt
        ├── web/
        │   └── js/
        └── src/
            └── lbt/
                ├── boolean_and.py
                ├── combine_from_list.py
                ├── crop_by_mask.py
                ├── folder_info.py
                ├── image_combiner.py
                ├── image_loader.py
                ├── image_loader_from_list.py
                ├── image_loader_from_path.py
                ├── image_saver.py
                ├── list_info.py
                ├── multiline_text_loader.py
                ├── string_to_list.py
                ├── switch_no_pause.py
                ├── text_image_comparison.py
                ├── text_keyword_match.py
                ├── text_loader.py
                ├── video_loader.py
                └── video_saver.py
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
    - `image_sequence` (BOOLEAN): 
        - `True` (default): Saves each image in the batch as a numbered sequence (e.g., `filename_0000.png`, `filename_0001.png`).
        - `False`: Saves only the first image from the batch.
    - `overwrite` (BOOLEAN): If `True`, overwrites existing files. If `False`, it will find a new name by appending a number if the file already exists.
    - `format` (OPTIONAL ENUM: `png`, `jpg`, `jpeg`, `bmp`, `webp`): The image format to save as. Only used in `Relative` mode.
- **Behavior:** If `overwrite` is set to `False` and a file with the same name already exists, the node will automatically find a new name (e.g., `filename_1.png`, `filename_2.png`) to prevent overwriting.

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


### 11. Load Multiline Text (LBT)

- **Description:** Loads a text file from ComfyUI's input directory and splits it into multiple prompts by blank lines.
- **Inputs:**
    - `file` (FILE): A `.txt` file from the ComfyUI input directory.
- **Outputs:**
    - `prompt_batch` (STRING): All prompts joined by newlines.
    - `count` (INT): Number of prompts found.
    - `full_filename` (STRING): The full filename.
    - `filename_no_ext` (STRING): The filename without extension.

### 12. Convert String to List (LBT)

- **Description:** Converts a formatted string into a list of strings (LBTlist). The input must be in the format: `"count, item1, item2, ..."`.
- **Inputs:**
    - `text` (STRING): A comma-separated string with the first value being the item count.
- **Outputs:**
    - `lbt_list` (LBT_LIST): A list of strings.
- **Note:** The count in the string must match the actual number of items.

### 13. Get List Info (LBT)

- **Description:** Returns the size of an LBTlist and passes the list through.
- **Inputs:**
    - `lbt_list` (LBT_LIST): The input list.
- **Outputs:**
    - `count` (INT): Number of items in the list.
    - `lbt_list` (LBT_LIST): The original list.

### 14. Load Image from Path (LBT)

- **Description:** Loads an image from a given file path. If the file exists, returns the image and `True`; otherwise returns a 100×100 white placeholder image and `False`.
- **Inputs:**
    - `file_path` (STRING): Absolute path to the image file.
- **Outputs:**
    - `image` (IMAGE): The loaded image or a white placeholder.
    - `file_exists` (BOOLEAN): Whether the file was found.

### 15. Boolean AND (LBT)

- **Description:** Performs a logical AND operation on multiple boolean inputs. Supports 2 to 32 inputs. Unconnected inputs default to `True`.
- **Inputs:**
    - `input_count` (INT): Number of boolean inputs to evaluate (2–32).
    - `bool_1` ~ `bool_32` (BOOLEAN): Boolean values to AND together.
- **Outputs:**
    - `result` (BOOLEAN): `True` if all inputs are `True`, otherwise `False`.

### 16. Text Keyword Match (LBT)

- **Description:** Checks whether any of the given keywords appear in the input text. Case-insensitive by default.
- **Inputs:**
    - `text` (STRING): The text to search in.
    - `keywords` (STRING): Comma-separated keywords (e.g., `"cat, dog, bird"`).
    - `case_sensitive` (BOOLEAN): If `True`, matching is case-sensitive.
- **Outputs:**
    - `matched` (BOOLEAN): `True` if at least one keyword is found.

### 17. Save Video (LBT)

- **Description:** Saves a batch of image frames as an animated video file (gif/webp/mp4/avi/...). Based on VideoHelperSuite's VideoCombine with custom path handling and overwrite options.
- **Inputs:**
    - `images` (IMAGE): The image frames to save as a video.
    - `frame_rate` (FLOAT): Video frame rate (1–120 FPS, default 8).
    - `loop_count` (INT): Number of loops for gif/webp (0 = infinite).
    - `filename_text` (STRING): Output filename (without extension).
    - `save_path` (STRING): Directory to save the video.
    - `format` (ENUM): Output format (gif/webp/mp4/etc.), uses VHS video_formats.
    - `pingpong` (BOOLEAN): If `True`, plays the video forward then backward.
    - `overwrite` (BOOLEAN): If `True`, replaces existing files; otherwise auto-increments.
    - `audio` (OPTIONAL AUDIO): Audio track to mux into the video.
- **Outputs:**
    - `filepath` (STRING): Path to the saved video.
- **Note:** Requires `ffmpeg` or `imageio-ffmpeg` for video encoding (except gif/webp which use Pillow).

### 18. Switch No Pause (LBT)

- **Description:** A boolean-controlled switch that never pauses the workflow when the inactive branch is disconnected or encountered an error. Unlike the native Switch node, this gracefully handles missing connections.
- **Inputs:**
    - `boolean` (BOOLEAN): Selector — `True` forwards `on_true`, `False` forwards `on_false`.
    - `on_true` (ANY, optional): Value forwarded when boolean is `True`.
    - `on_false` (ANY, optional): Value forwarded when boolean is `False`.
- **Outputs:**
    - `output` (ANY): The selected value, or `None` if that branch is absent.
- **Note:** Both branches are lazy and optional — the workflow continues even if the inactive branch is disconnected or errored.

## Troubleshooting

- **Nodes not appearing:** Ensure the `1_Comfyui_LBT` folder is directly inside `ComfyUI/custom_nodes/` and you have restarted ComfyUI.
- **`ModuleNotFoundError` or `AttributeError`:** Make sure all dependencies are installed by running `pip install -r custom_nodes/1_Comfyui_LBT/requirements.txt` in your ComfyUI Python environment.
- **`KeyError: 'JPG'`:** This has been addressed in the latest version of `Save Image (LBT)`. Ensure your `requirements.txt` is up to date and you have restarted ComfyUI.
- **`Permission denied` errors:** Check if ComfyUI has the necessary read/write permissions for the specified `folder_path` or `save_path`.
- **Video loading issues:** Ensure `ffmpeg` is correctly installed and accessible by `comfyui-videohelpersuite` (which our video node relies on). Refer to `comfyui-videohelpersuite`'s documentation for `ffmpeg` setup.

If you encounter any other issues, please provide the full error message and steps to reproduce.
