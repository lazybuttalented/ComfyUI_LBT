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
    └── 1_Comfyui_LBT/          # 或 "Comfyui_LBT/"，取决于安装方式
        ├── __init__.py
        ├── requirements.txt
        ├── web/
        │   └── js/
        └── src/
            └── lbt/
                ├── boolean_and.py        # 布尔与节点
                ├── combine_from_list.py   # 从列表合并图片
                ├── crop_by_mask.py       # 根据遮罩裁剪图片
                ├── folder_info.py         # 获取文件夹信息
                ├── image_combiner.py      # 从批次合并图片
                ├── image_loader.py       # 从文件夹加载图片
                ├── image_loader_from_list.py  # 从列表加载图片
                ├── image_loader_from_path.py  # 从路径加载图片
                ├── image_saver.py         # 保存图片
                ├── list_info.py           # 获取列表信息
                ├── multiline_text_loader.py  # 加载多行文本
                ├── string_to_list.py      # 字符串转列表
                ├── switch_no_pause.py     # 开关无暂停
                ├── text_image_comparison.py   # 文本与图片库比对
                ├── text_keyword_match.py  # 文本关键词匹配
                ├── text_loader.py         # 从文件夹加载文本
                ├── video_loader.py        # 从文件夹加载视频
                └── video_saver.py         # 保存视频
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
    - `图像序列 (image_sequence)` (BOOLEAN):
        - `True` (默认): 将批次中的每张图片保存为带编号的序列 (例如, `filename_0000.png`, `filename_0001.png`)。
        - `False`: 仅保存批次中的第一张图片。
    - `覆盖 (overwrite)` (BOOLEAN): 如果为 `True`，则覆盖现有文件。如果为 `False`，且文件已存在，节点会自动通过附加数字来寻找新的文件名。
    - `格式 (format)` (OPTIONAL ENUM: `png`, `jpg`, `jpeg`, `bmp`, `webp`): 保存的图片格式。仅在 `Relative` (相对) 模式下使用。
- **行为 (Behavior):** 如果 `覆盖 (overwrite)` 设置为 `False` 且目标路径下已存在同名文件，节点将自动寻找新的文件名 (例如, `filename_1.png`, `filename_2.png`) 以防止覆盖。

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


### 11. 加载多行文本 (Load Multiline Text (LBT))

- **描述 (Description):** 从 ComfyUI 的 input 目录加载文本文件，并按空行分割为多个提示词。
- **输入 (Inputs):**
    - `文件 (file)` (FILE): ComfyUI input 目录下的 `.txt` 文件。
- **输出 (Outputs):**
    - `提示词批次 (prompt_batch)` (STRING): 所有提示词以换行符连接。
    - `数量 (count)` (INT): 找到的提示词数量。
    - `完整文件名 (full_filename)` (STRING): 完整文件名。
    - `无扩展名 (filename_no_ext)` (STRING): 不带扩展名的文件名。

### 12. 字符串转列表 (Convert String to List (LBT))

- **描述 (Description):** 将格式化的字符串转换为字符串列表（LBTlist）。输入格式为：`"数量, 项目1, 项目2, ..."`。
- **输入 (Inputs):**
    - `文本 (text)` (STRING): 逗号分隔的字符串，第一个值为项目数量。
- **输出 (Outputs):**
    - `LBT列表 (lbt_list)` (LBT_LIST): 字符串列表。
- **注意 (Note):** 字符串中的数量必须与实际项目数量一致。

### 13. 获取列表信息 (Get List Info (LBT))

- **描述 (Description):** 返回 LBTlist 的大小并透传列表。
- **输入 (Inputs):**
    - `LBT列表 (lbt_list)` (LBT_LIST): 输入的列表。
- **输出 (Outputs):**
    - `数量 (count)` (INT): 列表中的项目数量。
    - `LBT列表 (lbt_list)` (LBT_LIST): 原始列表。

### 14. 从路径加载图片 (Load Image from Path (LBT))

- **描述 (Description):** 从指定文件路径加载图片。如果文件存在，返回图片和 `True`；否则返回一个 100×100 白色占位图和 `False`。
- **输入 (Inputs):**
    - `文件路径 (file_path)` (STRING): 图片文件的绝对路径。
- **输出 (Outputs):**
    - `图像 (image)` (IMAGE): 加载的图片或白色占位图。
    - `文件存在 (file_exists)` (BOOLEAN): 文件是否被找到。

### 15. 布尔与 (Boolean AND (LBT))

- **描述 (Description):** 对多个布尔输入执行逻辑与运算。支持 2 到 32 个输入。未连接的输入默认为 `True`。
- **输入 (Inputs):**
    - `输入数量 (input_count)` (INT): 要计算的布尔输入数量（2–32）。
    - `布尔_1` ~ `布尔_32` (BOOLEAN): 要进行与运算的布尔值。
- **输出 (Outputs):**
    - `结果 (result)` (BOOLEAN): 所有输入都为 `True` 时返回 `True`，否则返回 `False`。

### 16. 文本关键词匹配 (Text Keyword Match (LBT))

- **描述 (Description):** 检查输入文本中是否包含指定的关键词。默认不区分大小写。
- **输入 (Inputs):**
    - `文本 (text)` (STRING): 要搜索的文本。
    - `关键词 (keywords)` (STRING): 逗号分隔的关键词（例如，`"猫, 狗, 鸟"`）。
    - `区分大小写 (case_sensitive)` (BOOLEAN): 如果为 `True`，则区分大小写。
- **输出 (Outputs):**
    - `匹配 (matched)` (BOOLEAN): 找到至少一个关键词时返回 `True`。

### 17. 保存视频 (Save Video (LBT))

- **描述 (Description):** 将一批图片帧保存为动画视频文件（gif/webp/mp4/avi/...）。基于 VideoHelperSuite 的 VideoCombine，支持自定义路径和覆盖选项。
- **输入 (Inputs):**
    - `图像 (images)` (IMAGE): 要保存为视频的图片帧。
    - `帧率 (frame_rate)` (FLOAT): 视频帧率（1–120 FPS，默认 8）。
    - `循环次数 (loop_count)` (INT): gif/webp 的循环次数（0 = 无限）。
    - `文件名称 (filename_text)` (STRING): 输出文件名（不含扩展名）。
    - `保存路径 (save_path)` (STRING): 保存视频的目录。
    - `格式 (format)` (ENUM): 输出格式（gif/webp/mp4 等），使用 VHS video_formats。
    - `乒乓播放 (pingpong)` (BOOLEAN): 如果为 `True`，视频先正向播放再反向播放。
    - `覆盖 (overwrite)` (BOOLEAN): 如果为 `True`，覆盖现有文件；否则自动递增编号。
    - `音频 (audio)` (OPTIONAL AUDIO): 要混入视频的音轨。
- **输出 (Outputs):**
    - `文件路径 (filepath)` (STRING): 保存的视频路径。
- **注意 (Note):** 视频编码需要 `ffmpeg` 或 `imageio-ffmpeg`（gif/webp 使用 Pillow，无需 ffmpeg）。

### 18. 开关无暂停 (Switch No Pause (LBT))

- **描述 (Description):** 一个布尔值控制的开关，与原生 Switch 节点不同的是：当非活动分支断连或出错时，不会暂停工作流。优雅地处理缺失的连接。
- **输入 (Inputs):**
    - `布尔值 (boolean)` (BOOLEAN): 选择器 — `True` 转发 `真分支`，`False` 转发 `假分支`。
    - `真分支 (on_true)` (ANY, optional): 布尔值为 `True` 时转发的值。
    - `假分支 (on_false)` (ANY, optional): 布尔值为 `False` 时转发的值。
- **输出 (Outputs):**
    - `输出 (output)` (ANY): 选中的值，如果该分支不存在则为 `None`。
- **注意 (Note):** 两个分支都是 lazy 和 optional 的 — 即使非活动分支断连或出错，工作流也会继续执行。

## 故障排查

- **节点不显示:** 确保 `1_Comfyui_LBT` 文件夹直接位于 `ComfyUI/custom_nodes/` 内，并且您已经重启了 ComfyUI。
- **`ModuleNotFoundError` 或 `AttributeError`:** 确保在您的 ComfyUI Python 环境中运行 `pip install -r custom_nodes/1_Comfyui_LBT/requirements.txt` 来安装所有依赖项。
- **`KeyError: 'JPG'`:** 这个问题已在最新版的 `Save Image (LBT)` 中解决。请确保您的 `requirements.txt` 是最新的，并已重启 ComfyUI。
- **`Permission denied` (权限被拒绝) 错误:** 检查 ComfyUI 是否对指定的 `folder_path` 或 `save_path` 具有必要的读/写权限。
- **视频加载问题:** 确保 `ffmpeg` 已正确安装并且可被 `comfyui-videohelpersuite`（我们的视频节点所依赖的库）访问。有关 `ffmpeg` 的设置，请参考 `comfyui-videohelpersuite` 的文档。

如果您遇到任何其他问题，请提供完整的错误信息和复现步骤。
