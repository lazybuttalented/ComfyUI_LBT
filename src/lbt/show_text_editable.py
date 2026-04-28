"""
LBT_ShowTextEditable — Show Text Editable (LBT)

Extends the classic ShowText pattern with an editable text box and a reset button.

Widget layout (node UI):
  [0] text_display  — read-only preview (mirrors upstream text)
  [1] text_edit_vis — visible editable box
       ↺ Reset to input (button: resets edit box to upstream text)
  (hidden auto widget "text_edit" — invisible, serialised to prompt)

Inputs:
  - text (STRING, forceInput): upstream text
  - text_edit (STRING): editable box content, serialised by frontend via the
    hidden auto widget so the backend receives the live user-edited value

Outputs:
  - text       : passthrough (same as upstream input)
  - text_edited: current value of the editable box

Frontend responsibilities (lbt_show_text_editable.js):
  1. Locate and hide the auto-generated text_edit widget.
  2. Insert text_display (read-only) before it.
  3. Insert visible edit box after it, syncing its value to the hidden widget
     on every input/change event.
  4. Add a "↺ Reset to input" button that copies text_display value into
     both the visible edit box and the hidden auto widget.
  5. On onExecuted: always refresh text_display; overwrite the edit box
     only if the upstream text changed since the last run.
"""


class LBT_ShowTextEditable:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text":      ("STRING", {"forceInput": True}),
                # text_edit is the editable widget sent from the frontend.
                # The frontend hides ComfyUI's auto-rendered widget for this
                # and instead manages a visible custom widget whose value is
                # kept in sync with this hidden slot.
                "text_edit": ("STRING", {"multiline": True, "default": ""}),
            },
            "hidden": {
                "unique_id":     "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "text_edited")
    FUNCTION     = "execute"
    OUTPUT_NODE  = True
    CATEGORY     = "LBT"

    def execute(
        self,
        text: str,
        text_edit: str = "",
        unique_id=None,
        extra_pnginfo=None,
    ):
        # text_edit arrives directly from the frontend widget serialisation.
        # We just need to persist it back so the frontend can restore it
        # on workflow load.
        if unique_id is not None and extra_pnginfo is not None:
            if (
                isinstance(extra_pnginfo, list)
                and isinstance(extra_pnginfo[0], dict)
                and "workflow" in extra_pnginfo[0]
            ):
                workflow = extra_pnginfo[0]["workflow"]
                node = next(
                    (x for x in workflow["nodes"]
                     if str(x["id"]) == str(unique_id)),
                    None,
                )
                if node is not None:
                    # widgets_values layout the frontend relies on:
                    #   [0] = text_edit (the hidden auto widget ComfyUI renders)
                    #   [1] = text_display value (read-only preview — not used by backend)
                    # We leave widgets_values alone; the frontend manages it.
                    pass

        return {
            "ui": {
                # Sent to the frontend so it can refresh text_display and
                # decide whether to overwrite the visible edit box.
                "text": [text],
            },
            "result": (text, text_edit),
        }


NODE_CLASS_MAPPINGS = {
    "LBT_ShowTextEditable": LBT_ShowTextEditable,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_ShowTextEditable": "Show Text Editable (LBT)",
}
