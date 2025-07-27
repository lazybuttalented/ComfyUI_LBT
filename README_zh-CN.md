# LBT ComfyUI 自定义节点

这个仓库包含了一系列为 ComfyUI 设计的自定义节点，旨在增强图片和视频处理的工作流。

## 安装指南

请遵循以下步骤来安装自定义节点及其依赖项。

### 1. 放置自定义节点文件夹

导航到您的 ComfyUI 安装目录，找到 `custom_nodes` 文件夹。
将整个 `1_Comfyui_LBT` 文件夹（即包含此文件的文件夹）放入 `ComfyUI/custom_nodes/` 目录中。

您的目录结构应该如下所示：

```
ComfyUI/
└── custom_nodes/
    └── 1_Comfyui_LBT/
        ├── __init__.py
        ├── requirements.txt
        └── src/
            └── lbt/
                ├── ... (节点文件)
```

### 2. 安装依赖项

这些自定义节点需要一些额外的 Python 库。

打开命令提示符或终端，导航到您的 ComfyUI 安装根目录（即 `main.py` 所在的目录）。

请确保您处于 ComfyUI 所使用的 Python 环境中。这可能需要激活一个虚拟环境（virtual environment）。如果您不确定如何操作，请参考您的 ComfyUI 安装指南。

激活环境后，使用 `pip` 来安装所需的包：

```bash
pip install -r custom_nodes/1_Comfyui_LBT/requirements.txt
```

### 3. 重启 ComfyUI

安装完依赖项后，您**必须**重启您的 ComfyUI 应用，新的节点才会出现并正常工作。

## 节点列表

安装并重启 ComfyUI 后，您可以在界面上通过右键单击画布来找到这些节点。

### 1. 从文件夹加载图片 (Load Image From Folder (LBT))

- **描述 (Description):** 根据索引（种子）从指定文件夹加载单张图片。对于需要从目录中逐一处理图片的场景非常有用。
- **输入 (Inputs):**
    - `文件夹路径 (folder_path)` (STRING): 包含图片的文件夹的绝对路径。
    - `种子 (seed)` (INT): 一个决定加载哪张图片的整数。此输入默认为 `Increment`（递增），意味着每次执行工作流时，它会自动加载文件夹中的下一张图片。
- **输出 (Outputs):**
    - `图像 (image)` (IMAGE): 加载的图片。
    - `完整文件名 (full_filename)` (STRING): 加载图片的完整文件名 (例如, `image001.png`)。
    - `无扩展名 (filename_no_ext)` (STRING): 不带扩展名的文件名 (例如, `image001`)。

### 2. 保存图片 (Save Image (LBT))

- **描述 (Description):** 使用灵活的命名选项将图片保存到指定路径。
- **输入 (Inputs):**
    - `图像 (images)` (IMAGE): 需要保存的图片。
    - `文件名称 (filename_text)` (STRING): 根据 `模式 (mode)` 的不同，可以是基础文件名或完整路径。
    - `保存路径 (save_path)` (STRING): 图片将被保存的目录。
    - `模式 (mode)` (ENUM: `Relative` (相对), `Absolute` (绝对)):
        - `Relative` (相对): 使用 `文件名称 (filename_text)` 作为基础名称，并附加所选的 `格式 (format)` 扩展名。
        - `Absolute` (绝对): 使用 `文件名称 (filename_text)` 作为完整文件名（包含扩展名），并自动从中检测保存格式。`保存路径 (save_path)` 仍作为基础目录使用。
    - `格式 (format)` (OPTIONAL ENUM: `png`, `jpg`, `jpeg`, `bmp`, `webp`): 保存的图片格式。仅在 `Relative` (相对) 模式下使用。
- **行为 (Behavior):** 如果目标路径下已存在同名文件，节点将报错以防止覆盖。

### 3. 获取文件夹信息 (Get Folder Info (LBT))

- **描述 (Description):** 扫描指定文件夹并输出图片、视频和文本文件的数量。
- **输入 (Inputs):**
    - `文件夹路径 (folder_path)` (STRING): 需要扫描的文件夹的绝对路径。
- **输出 (Outputs):**
    - `图片数量 (image_count)` (INT): 找到的图片文件数量。
    - `视频数量 (video_count)` (INT): 找到的视频文件数量。
    - `文本数量 (txt_count)` (INT): 找到的文本文件数量。
- **注意 (Note):** 要查看输出，您需要将这些输出连接到一个显示节点（例如，一个 `Primitive` 节点或来自其他自定义节点包的 `Show Text` 节点）并运行一次工作流。

### 4. 从文件夹加载视频 (Load Video From Folder (LBT))

- **描述 (Description):** 根据索引（种子）从指定文件夹加载视频的第一帧。
- **输入 (Inputs):**
    - `文件夹路径 (folder_path)` (STRING): 包含视频文件的文件夹的绝对路径。
    - `种子 (seed)` (INT): 一个决定加载哪个视频的整数。此输入默认为 `Increment`（递增），意味着每次执行工作流时，它会自动加载文件夹中下一个视频的第一帧。
- **输出 (Outputs):**
    - `图像 (image)` (IMAGE): 加载视频的第一帧作为图像。
    - `完整文件名 (full_filename)` (STRING): 加载视频的完整文件名 (例如, `video001.mp4`)。
    - `无扩展名 (filename_no_ext)` (STRING): 不带扩展名的文件名 (例如, `video001`)。
    - `音频 (audio)` (AUDIO): 音频数据的占位符（当前为空）。
    - `视频信息 (video_info)` (VHS_VIDEOINFO): 视频元数据的占位符（当前为空）。

### 5. 从文件夹加载文本 (Load Text From Folder (LBT))

- **描述 (Description):** 根据索引（种子）从指定文件夹加载单个文本文件 (`.txt`)。
- **输入 (Inputs):**
    - `文件夹路径 (folder_path)` (STRING): 包含文本文件的文件夹的绝对路径。
    - `种子 (seed)` (INT): 一个决定加载哪个文本文件的整数。此输入默认为 `Increment`（递增），意味着每次执行工作流时，它会自动加载文件夹中的下一个文件。
- **输出 (Outputs):**
    - `文本 (text)` (STRING): 加载的文本文件的内容。
    - `完整文件名 (full_filename)` (STRING): 加载文本文件的完整文件名 (例如, `document.txt`)。
    - `无扩展名 (filename_no_ext)` (STRING): 不带扩展名的文件名 (例如, `document`)。

### 6. 从列表加载图片 (Load Images From List (LBT))

- **描述 (Description):** 根据提供的文件名列表（不含扩展名）从文件夹中加载多张图片。它可以自动调整图片尺寸以匹配第一张加载的图片的尺寸。
- **输入 (Inputs):**
    - `LBT列表 (lbt_list)` (LBT_LIST): 需要加载的文件名列表 (例如, 来自 `Convert String to List` 节点)。
    - `文件夹路径 (folder_path)` (STRING): 包含图片的文件夹的绝对路径。
    - `调整模式 (resize_mode)` (ENUM: `Pad` (填充), `Crop` (裁剪), `Stretch` (拉伸), `None` (无)):
        - `Pad` (填充): 在保持长宽比的同时调整尺寸，并用黑色填充空白区域。
        - `Crop` (裁剪): 调整尺寸并裁剪图片以适应目标尺寸。
        - `Stretch` (拉伸): 忽略长宽比，将图片拉伸至目标尺寸。
        - `None` (无): 跳过尺寸不同的图片。
- **输出 (Outputs):**
    - `图像 (image)` (IMAGE): 一批已加载并处理过的图片。

### 7. 根据遮罩裁剪图片 (Crop Image by Mask (LBT))

- **描述 (Description):** 将图片裁剪到其遮罩的边界框。它可以使用外部遮罩或图片自身的 Alpha 通道。
- **输入 (Inputs):**
    - `图像 (image)` (IMAGE): 需要被裁剪的图片。
    - `偏移量 (offset)` (INT): 一个用于扩展（正值）或收缩（负值）裁剪区域的整数。
    - `遮罩 (mask)` (OPTIONAL MASK): 用于定义裁剪区域的外部遮罩。如果未提供，节点将使用图片的 Alpha 通道。
- **输出 (Outputs):**
    - `图像 (image)` (IMAGE LIST): 一个裁剪后的图片列表。输出是列表因为批次中的每张图片都可能被裁剪成不同的尺寸。
- **行为 (Behavior):** 如果提供了外部遮罩，其尺寸必须与图片尺寸匹配，否则节点将报错。

### 8. 从批次合并图片 (Combine Images From Batch (LBT))

- **描述 (Description):** 将一批**尺寸相同**的图片合并成一张大图。
- **输入 (Inputs):**
    - `图像 (images)` (IMAGE): 一批图片。所有图片必须具有相同的尺寸。
    - `方向 (direction)` (ENUM: `horizontal` (水平), `vertical` (垂直), `most_compact` (最密))。
    - `调整模式 (resize_mode)` (ENUM: `Pad` (填充), `Stretch` (拉伸), `None` (无)): 在合并前统一图片尺寸的方法。推荐使用 `Pad` (填充)。
    - `间距 (spacing)` (INT): 在图片之间添加的像素间隙。
    - `保留Alpha (keep_alpha)` (BOOLEAN): 如果勾选，将保留透明度并输出 RGBA 图像。如果未勾选，图像将被平铺在纯色背景上。
    - `背景颜色 (bg_color)` (STRING): 背景的十六进制颜色代码 (例如, `#000000`)。仅在 `保留Alpha (keep_alpha)` 未勾选时生效。
- **输出 (Outputs):**
    - `图像 (image)` (IMAGE): 最终合并的图片。

### 9. 从列表合并图片 (Combine Images From List (LBT))

- **描述 (Description):** 一个强大的节点，可将一个包含**不同尺寸**图片的列表（例如, 来自 `Crop Image by Mask`）排列成一张合成图。
- **输入 (Inputs):**
    - `图像 (images)` (IMAGE LIST): 需要合并的图片列表。
    - `方向 (direction)` (ENUM: `horizontal` (水平), `vertical` (垂直), `most_compact` (最密))。
    - `间距 (spacing)` (INT): 在图片之间添加的像素间隙。
    - `对齐方式 (alignment)` (ENUM: `center` (居中), `start` (起始), `end` (末尾))。
    - `保留Alpha (keep_alpha)` (BOOLEAN): 如果勾选，将保留透明度并输出 RGBA 图像。如果未勾选，图像将被平铺在纯色背景上。
    - `背景颜色 (bg_color)` (STRING): 背景的十六进制颜色代码 (例如, `#000000`)。仅在 `保留Alpha (keep_alpha)` 未勾选时生效。
- **输出 (Outputs):**
    - `图像 (image)` (IMAGE): 最终合并的图片。

### 10. 文本与图片库比对 (Text Image Library Comparison (LBT))

- **描述 (Description):** 扫描一段文本，以查找在指定文件夹中的图片文件名的提及。然后输出找到的唯一文件名的列表，非常适合用于根据剧本或故事动态加载图片。
- **输入 (Inputs):**
    - `文本 (text)` (STRING): 需要分析的文本。
    - `文件夹路径 (folder_path)` (STRING): 包含您的图片库的文件夹路径。
- **输出 (Outputs):**
    - `LBT列表 (lbt_list)` (LBT_LIST): 在文本中被提及的唯一图片文件名（不含扩展名）的列表。
    - `独立文件数量 (unique_found_count)` (INT): 找到的唯一图片的数量。
    - `总提及次数 (total_mentions)` (INT): 图片库中所有图片在文本中被提及的总次数。
- **行为 (Behavior):** 搜索不区分大小写，且仅匹配整个单词。


## 故障排查

- **节点不显示:** 确保 `1_Comfyui_LBT` 文件夹直接位于 `ComfyUI/custom_nodes/` 内，并且您已经重启了 ComfyUI。
- **`ModuleNotFoundError` 或 `AttributeError`:** 确保在您的 ComfyUI Python 环境中运行 `pip install -r custom_nodes/1_Comfyui_LBT/requirements.txt` 来安装所有依赖项。
- **`KeyError: 'JPG'`:** 这个问题已在最新版的 `Save Image (LBT)` 中解决。请确保您的 `requirements.txt` 是最新的，并已重启 ComfyUI。
- **`Permission denied` (权限被拒绝) 错误:** 检查 ComfyUI 是否对指定的 `folder_path` 或 `save_path` 具有必要的读/写权限。
- **视频加载问题:** 确保 `ffmpeg` 已正确安装并且可被 `comfyui-videohelpersuite`（我们的视频节点所依赖的库）访问。有关 `ffmpeg` 的设置，请参考 `comfyui-videohelpersuite` 的文档。

如果您遇到任何其他问题，请提供完整的错误信息和复现步骤。
