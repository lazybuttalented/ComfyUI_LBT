"""
LBT_SaveVideo — Save Video (LBT)
Based on VideoHelperSuite's VideoCombine, with:
  - filename_text + save_path instead of filename_prefix under output dir
  - overwrite option (True = replace existing file, False = auto-increment suffix)
  - meta_batch and vae inputs removed
  - format-driven output (gif / webp via Pillow; all others via ffmpeg)
"""

import os
import sys
import json
import subprocess
import datetime
import re
import time
import itertools

import numpy as np
import torch
from PIL import Image, ExifTags
from PIL.PngImagePlugin import PngInfo
from pathlib import Path

import folder_paths
from comfy.utils import ProgressBar

# ─── Locate the VHS video_formats directory ──────────────────────────────────
# Scan directly from the filesystem so we don't depend on VHS load order.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up to custom_nodes (src/lbt -> src -> <plugin_root> -> custom_nodes)
_CUSTOM_NODES_DIR = os.path.normpath(os.path.join(_THIS_DIR, "..", "..", ".."))
# Try to find VHS in custom_nodes (works regardless of this plugin's folder name)
_VHS_FORMATS_DIR = ""
for entry in os.scandir(_CUSTOM_NODES_DIR):
    if entry.is_dir() and entry.name.lower() == "comfyui-videohelpersuite":
        _VHS_FORMATS_DIR = os.path.join(entry.path, "video_formats")
        break

def _lbt_get_video_formats():
    """
    Scan VHS video_formats/*.json directly, independent of VHS import order.
    Returns (formats_list, format_widgets_dict) in the same shape as VHS's
    get_video_formats().
    """
    formats = []
    format_widgets = {}

    if not os.path.isdir(_VHS_FORMATS_DIR):
        return formats, format_widgets

    for entry in sorted(os.scandir(_VHS_FORMATS_DIR), key=lambda e: e.name):
        if not entry.is_file() or not entry.name.endswith(".json"):
            continue
        fmt_name = entry.name[:-5]          # strip .json
        try:
            with open(entry.path, "r") as f:
                vf = json.load(f)
        except Exception:
            continue

        # Skip gifski formats if gifski is unavailable (checked later).
        # We include them here — the runtime check will raise if needed.
        formats.append("video/" + fmt_name)

        # Collect extra_widgets declared in the format JSON
        widgets = []
        if "extra_widgets" in vf:
            widgets.extend(vf["extra_widgets"])
        if widgets:
            format_widgets["video/" + fmt_name] = widgets

    return formats, format_widgets


def _lbt_apply_format_widgets(format_name: str, kwargs: dict) -> dict:
    """
    Read the format JSON and substitute widget values from kwargs.
    Falls back to VHS's apply_format_widgets if available; otherwise
    does a minimal substitution sufficient for most formats.
    """
    if _VHS_AVAILABLE:
        try:
            return _vhs_apply_format_widgets(format_name, kwargs)
        except Exception:
            pass

    fmt_path = os.path.join(_VHS_FORMATS_DIR, format_name + ".json")
    if not os.path.exists(fmt_path):
        return {}
    with open(fmt_path, "r") as f:
        vf = json.load(f)

    # Resolve widget definitions to their default values
    def _resolve_widget(val):
        if not isinstance(val, list) or len(val) < 2:
            return val
        key = val[0]
        # If user provided value in kwargs, use it
        if key in kwargs:
            return kwargs[key]
        # Otherwise use default based on widget type
        opt = val[1]
        if isinstance(opt, list):
            # Enum: [key, [option1, option2, ...]] -> first option
            return opt[0] if opt else ""
        if opt in ("INT", "FLOAT") and len(val) >= 3:
            return val[2].get("default", 0)
        if opt == "BOOLEAN" and len(val) >= 3:
            return val[2].get("default", False)
        return val

    def _deep_resolve(obj):
        if isinstance(obj, dict):
            return {k: _deep_resolve(v) for k, v in obj.items()}
        if isinstance(obj, list):
            # Check if this list is a widget definition
            resolved = _resolve_widget(obj)
            if resolved is not obj:  # It was a widget, return resolved value
                return resolved
            # Otherwise recursively resolve each element
            return [_deep_resolve(v) for v in obj]
        return obj

    vf = _deep_resolve(vf)

    # Flatten main_pass: ensure all values are strings
    def _flatten_pass(pass_list):
        flat = []
        for item in pass_list:
            if isinstance(item, list):
                flat.extend(str(x) for x in item)
            else:
                flat.append(str(item))
        return flat

    for key in ("main_pass", "pre_pass", "inputs_main_pass", "audio_pass"):
        if key in vf and isinstance(vf[key], list):
            vf[key] = _flatten_pass(vf[key])

    return vf


# ─── Locate ffmpeg ───────────────────────────────────────────────────────────
# Try imageio-ffmpeg first (same as VHS), then system PATH
def _find_ffmpeg():
    """Find ffmpeg executable, prioritizing imageio-ffmpeg."""
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        return get_ffmpeg_exe()
    except Exception:
        pass
    import shutil
    return shutil.which("ffmpeg")

ffmpeg_path = _find_ffmpeg()
print(f"[LBT_SaveVideo] ffmpeg_path detected: {ffmpeg_path}")
gifski_path = os.environ.get("VHS_GIFSKI") or os.environ.get("JOV_GIFSKI")
ENCODE_ARGS = ("utf-8", "backslashreplace")

# ─── Try to import runtime helpers from VHS ──────────────────────────────────
# We only need tensor helpers and the process generators.
# ffmpeg_path is already set above, VHS import is optional for extras.
_VHS_AVAILABLE = False
try:
    from videohelpersuite.nodes import (
        apply_format_widgets as _vhs_apply_format_widgets,
        tensor_to_bytes, tensor_to_shorts,
        to_pingpong, ffmpeg_process, gifski_process,
    )
    from videohelpersuite.utils import merge_filter_args
    _VHS_AVAILABLE = True
except Exception:
    pass

if not _VHS_AVAILABLE:
    # ffmpeg_path is already set by _find_ffmpeg() above, don't overwrite it
    # gifski_path is already set above
    ENCODE_ARGS = ("utf-8", "backslashreplace")

    def _vhs_apply_format_widgets(fmt, kwargs):
        return {}

    def tensor_to_bytes(tensor):
        arr = tensor.cpu().numpy() * 255 + 0.5
        return np.clip(arr, 0, 255).astype(np.uint8)

    def tensor_to_shorts(tensor):
        arr = tensor.cpu().numpy() * 65535 + 0.5
        return np.clip(arr, 0, 65535).astype(np.uint16)

    def to_pingpong(inp):
        if not hasattr(inp, "__getitem__"):
            inp = list(inp)
        yield from inp
        for i in range(len(inp) - 2, 0, -1):
            yield inp[i]

    def ffmpeg_process(args, video_format, video_metadata, file_path, env):
        frame_data = yield
        total_frames_output = 0
        with subprocess.Popen(args + [file_path], stderr=subprocess.PIPE,
                              stdin=subprocess.PIPE, env=env) as proc:
            try:
                while frame_data is not None:
                    proc.stdin.write(frame_data)
                    frame_data = yield
                    total_frames_output += 1
                proc.stdin.flush()
                proc.stdin.close()
                res = proc.stderr.read()
            except BrokenPipeError:
                res = proc.stderr.read()
                raise Exception("An error occurred in the ffmpeg subprocess:\n"
                                + res.decode(*ENCODE_ARGS))
        yield total_frames_output
        if res:
            print(res.decode(*ENCODE_ARGS), end="", file=sys.stderr)

    def gifski_process(*args, **kwargs):
        raise NotImplementedError("gifski not available")

    def merge_filter_args(args, key="-vf"):
        pass


# ─── Helper ─────────────────────────────────────────────────────────────────

def _resolve_output_path(save_path: str, filename_text: str,
                         ext: str, overwrite: bool) -> str:
    """
    Build the full output file path.

    save_path   : directory (created if missing)
    filename_text: stem, no extension
    ext         : without leading dot
    overwrite   : if False and file exists, append _001, _002, …
    """
    os.makedirs(save_path, exist_ok=True)
    stem = filename_text.strip()
    base = os.path.join(save_path, f"{stem}.{ext}")

    if overwrite or not os.path.exists(base):
        return base

    # Auto-increment suffix
    counter = 1
    while True:
        candidate = os.path.join(save_path, f"{stem}_{counter:03d}.{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


# ─── Node ────────────────────────────────────────────────────────────────────

class LBT_SaveVideo:
    """Save a batch of IMAGE frames as an animated file (gif / webp / mp4 / …)."""

    @classmethod
    def INPUT_TYPES(cls):
        ffmpeg_formats, format_widgets = _lbt_get_video_formats()
        fmt_list = ["image/gif", "image/webp"] + ffmpeg_formats
        extra = {"formats": format_widgets} if format_widgets else {}
        return {
            "required": {
                "images": ("IMAGE",),
                "frame_rate": ("FLOAT", {"default": 8.0, "min": 1.0,
                                         "max": 120.0, "step": 0.5}),
                "loop_count": ("INT", {"default": 0, "min": 0,
                                       "max": 100, "step": 1}),
                "filename_text": ("STRING", {"default": "video_01",
                                             "multiline": False}),
                "save_path": ("STRING", {
                    "default": "./output"
                }),
                "format": (fmt_list, extra),
                "pingpong": ("BOOLEAN", {"default": False}),
                "overwrite": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "audio": ("AUDIO",),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)
    OUTPUT_NODE = True
    CATEGORY = "LBT"
    FUNCTION = "save_video"

    @classmethod
    def IS_CHANGED(cls, images, frame_rate, loop_count, filename_text,
                   save_path, format, pingpong, overwrite,
                   audio=None, prompt=None, extra_pnginfo=None, **kwargs):
        if overwrite:
            return time.time()
        return False

    def save_video(
        self,
        images,
        frame_rate: float,
        loop_count: int,
        filename_text: str,
        save_path: str,
        format: str,
        pingpong: bool,
        overwrite: bool,
        audio=None,
        prompt=None,
        extra_pnginfo=None,
        **kwargs,          # absorbs extra_widgets from format definitions
    ):
        if images is None or (isinstance(images, torch.Tensor) and images.size(0) == 0):
            return {"ui": {"gifs": []}, "result": ("",)}

        num_frames = len(images)
        pbar = ProgressBar(num_frames)

        first_image = images[0]
        images_iter = iter(images)

        # ── Metadata ────────────────────────────────────────────────────────
        metadata = PngInfo()
        video_metadata: dict = {}
        if prompt is not None:
            metadata.add_text("prompt", json.dumps(prompt))
            video_metadata["prompt"] = json.dumps(prompt)
        if extra_pnginfo is not None:
            for k, v in extra_pnginfo.items():
                metadata.add_text(k, json.dumps(v))
                video_metadata[k] = v
        metadata.add_text("CreationTime",
                          datetime.datetime.now().isoformat(" ")[:19])

        format_type, format_ext = format.split("/")

        # ── Resolve output path ─────────────────────────────────────────────
        if format_type == "image":
            ext = format_ext          # gif / webp
        else:
            # For ffmpeg formats we need the extension from the format JSON.
            # Apply widgets first so we can read 'extension'.
            video_format = _lbt_apply_format_widgets(format_ext, dict(kwargs))
            ext = video_format.get("extension", format_ext)

        file_path = _resolve_output_path(save_path, filename_text.strip(),
                                         ext, overwrite)

        # ── Save ────────────────────────────────────────────────────────────
        output_files = [file_path]

        if format_type == "image":
            # ── Pillow path (gif / webp) ─────────────────────────────────
            image_kwargs: dict = {}
            if format_ext == "gif":
                image_kwargs["disposal"] = 2
            if format_ext == "webp":
                exif = Image.Exif()
                exif[ExifTags.IFD.Exif] = {
                    36867: datetime.datetime.now().isoformat(" ")[:19]
                }
                image_kwargs["exif"] = exif
                image_kwargs["lossless"] = kwargs.get("lossless", True)

            frames_iter = images_iter
            if pingpong:
                frames_iter = to_pingpong(list(frames_iter))

            def _frames_gen(it):
                for img in it:
                    pbar.update(1)
                    yield Image.fromarray(tensor_to_bytes(img))

            frames = _frames_gen(frames_iter)
            first_pil = next(frames)
            first_pil.save(
                file_path,
                format=format_ext.upper(),
                save_all=True,
                append_images=frames,
                duration=round(1000 / frame_rate),
                loop=loop_count,
                compress_level=4,
                **image_kwargs,
            )

        else:
            # ── FFmpeg path ──────────────────────────────────────────────
            if ffmpeg_path is None:
                raise ProcessLookupError(
                    "ffmpeg is required for video outputs but could not be found.\n"
                    "Install imageio-ffmpeg, place an ffmpeg executable in the "
                    "working directory, or add ffmpeg to PATH."
                )

            # video_format was built above; re-merge kwargs in case needed
            video_format = _lbt_apply_format_widgets(format_ext, dict(kwargs))

            has_alpha = first_image.shape[-1] == 4
            kwargs["has_alpha"] = has_alpha
            video_format = _lbt_apply_format_widgets(format_ext, dict(kwargs))

            dim_alignment = video_format.get("dim_alignment", 2)
            h, w = first_image.shape[0], first_image.shape[1]
            if (w % dim_alignment) or (h % dim_alignment):
                to_pad = (-w % dim_alignment, -h % dim_alignment)
                padding = (
                    to_pad[0] // 2, to_pad[0] - to_pad[0] // 2,
                    to_pad[1] // 2, to_pad[1] - to_pad[1] // 2,
                )
                padfunc = torch.nn.ReplicationPad2d(padding)
                def _pad(image):
                    return padfunc(
                        image.permute(2, 0, 1).to(dtype=torch.float32)
                    ).permute(1, 2, 0)
                images_iter = map(_pad, images_iter)
                dimensions = (w + to_pad[0], h + to_pad[1])
                print("[LBT_SaveVideo] Warning: frames padded to fit codec alignment")
            else:
                dimensions = (w, h)

            if pingpong:
                images_iter = to_pingpong(list(images_iter))
                if num_frames > 2:
                    num_frames += num_frames - 2
                    pbar.total = num_frames

            loop_args = (
                ["-vf", f"loop=loop={loop_count}:size={num_frames}"]
                if loop_count > 0 else []
            )

            if video_format.get("input_color_depth", "8bit") == "16bit":
                images_iter = map(tensor_to_shorts, images_iter)
                i_pix_fmt = "rgba64" if has_alpha else "rgb48"
            else:
                images_iter = map(tensor_to_bytes, images_iter)
                i_pix_fmt = "rgba" if has_alpha else "rgb24"

            bitrate_arg = []
            bitrate = video_format.get("bitrate")
            if bitrate is not None:
                suffix = "M" if video_format.get("megabit") == "True" else "K"
                bitrate_arg = ["-b:v", f"{bitrate}{suffix}"]

            args = [
                ffmpeg_path, "-v", "error",
                "-y" if overwrite else "-n",  # -y = overwrite, -n = no overwrite
                "-f", "rawvideo", "-pix_fmt", i_pix_fmt,
                "-color_range", "pc", "-colorspace", "rgb",
                "-color_primaries", "bt709",
                "-color_trc", video_format.get("fake_trc", "iec61966-2-1"),
                "-s", f"{dimensions[0]}x{dimensions[1]}",
                "-r", str(frame_rate),
                "-i", "-",
            ] + loop_args

            def _to_bytes(x):
                if hasattr(x, 'numpy'):
                    x = x.numpy()
                return x.tobytes()
            images_iter = map(_to_bytes, images_iter)
            env = os.environ.copy()
            if "environment" in video_format:
                env.update(video_format["environment"])

            if "pre_pass" in video_format:
                images_list = [b"".join(images_iter)]
                os.makedirs(folder_paths.get_temp_directory(), exist_ok=True)
                in_args_len = args.index("-i") + 2
                pre_pass_args = args[:in_args_len] + video_format["pre_pass"]
                merge_filter_args(pre_pass_args)
                try:
                    subprocess.run(pre_pass_args, input=images_list[0],
                                   env=env, capture_output=True, check=True)
                except subprocess.CalledProcessError as e:
                    raise Exception("ffmpeg pre-pass error:\n"
                                    + e.stderr.decode(*ENCODE_ARGS))
                images_iter = iter(images_list)

            if "inputs_main_pass" in video_format:
                in_args_len = args.index("-i") + 2
                args = (args[:in_args_len]
                        + video_format["inputs_main_pass"]
                        + args[in_args_len:])

            if "gifski_pass" in video_format:
                output_process = gifski_process(
                    args, dimensions, frame_rate, video_format, file_path, env
                )
                audio = None
            else:
                # Filter out -n/-y from main_pass (we already set it above)
                main_pass_filtered = [
                    arg for arg in video_format["main_pass"]
                    if arg not in ("-n", "-y")
                ]
                args += main_pass_filtered + bitrate_arg
                merge_filter_args(args)
                output_process = ffmpeg_process(
                    args, video_format, video_metadata, file_path, env
                )

            output_process.send(None)  # prime generator
            for frame in images_iter:
                pbar.update(1)
                output_process.send(frame)

            try:
                total_frames_output = output_process.send(None)
                output_process.send(None)
            except StopIteration:
                total_frames_output = num_frames

            # ── Mux audio if provided ────────────────────────────────────
            if audio is not None:
                try:
                    a_waveform = audio["waveform"]
                except Exception:
                    a_waveform = None

                if a_waveform is not None:
                    audio_ext = video_format.get("extension", format_ext)
                    stem = os.path.splitext(os.path.basename(file_path))[0]
                    # 使用临时文件保存无声视频，避免输入输出文件冲突
                    temp_file = os.path.join(save_path, f"{stem}_temp.{audio_ext}")
                    # 最终输出到原始路径
                    final_output_path = file_path
                    # 重命名无声视频到临时文件
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    os.rename(file_path, temp_file)

                    if "audio_pass" not in video_format:
                        print("[LBT_SaveVideo] Warning: format has no explicit "
                              "audio support, defaulting to libopus")
                        video_format["audio_pass"] = ["-c:a", "libopus"]

                    channels = a_waveform.size(1)
                    min_audio_dur = total_frames_output / frame_rate + 1
                    if video_format.get("trim_to_audio", "False") != "False":
                        apad = []
                    else:
                        apad = ["-af",
                                f"apad=whole_dur={min_audio_dur}"]

                    mux_args = [
                        ffmpeg_path, "-v", "error", "-y",
                        "-i", temp_file,
                        "-ar", str(audio["sample_rate"]),
                        "-ac", str(channels),
                        "-f", "f32le", "-i", "-",
                        "-c:v", "copy",
                    ] + video_format["audio_pass"] + apad + [
                        "-shortest", final_output_path
                    ]

                    audio_data = (
                        a_waveform.squeeze(0).transpose(0, 1)
                        .numpy().tobytes()
                    )
                    merge_filter_args(mux_args, "-af")
                    try:
                        res = subprocess.run(
                            mux_args, input=audio_data,
                            env=env, capture_output=True, check=True
                        )
                    except subprocess.CalledProcessError as e:
                        raise Exception(
                            "ffmpeg audio mux error:\n"
                            + e.stderr.decode(*ENCODE_ARGS)
                        )
                    if res.stderr:
                        print(res.stderr.decode(*ENCODE_ARGS),
                              end="", file=sys.stderr)
                    # 删除临时无声视频文件
                    if os.path.exists(temp_file):
                        os.remove(temp_file)

        # ── Preview / UI response ────────────────────────────────────────────
        subfolder = os.path.relpath(
            os.path.dirname(file_path),
            folder_paths.get_output_directory()
        )
        filename_out = os.path.basename(file_path)

        preview = {
            "filename": filename_out,
            "subfolder": subfolder,
            "type": "output",
            "format": format,
            "frame_rate": frame_rate,
        }

        print(f"[LBT_SaveVideo] Saved → {file_path}")
        return {"ui": {"gifs": [preview]}, "result": (file_path,)}


NODE_CLASS_MAPPINGS = {
    "LBT_SaveVideo": LBT_SaveVideo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_SaveVideo": "Save Video (LBT)",
}

# ═══════════════════════════════════════════════════════════════════════════════
# 以下文本可根据需要自行修改：
# Please install Video Helper Suite to use this node.
# ═══════════════════════════════════════════════════════════════════════════════
