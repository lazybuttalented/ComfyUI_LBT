"""
LBT_ShowTextEditable — Show Text Editable (LBT)

Extends the classic ShowText pattern with an editable text box:
  - text       : upstream STRING input (forceInput)
  - text_display: (frontend only) read-only preview that always mirrors `text`
  - text_edit   : (frontend widget, serialised as widgets_values[1])
                  editable by the user; auto-filled from `text` ONLY when
                  the upstream value changes between runs
  - text        : passthrough output (same as input)
  - text_edited : output the current value of the edit box

Backend responsibilities
  1. Receive `text` (the upstream value) and `text_edit` (the current widget value).
  2. Return both as outputs.
  3. Persist both values into the workflow JSON via `extra_pnginfo`.

Frontend responsibilities (see lbt_show_text_editable.js)
  1. Keep text_display in sync with the latest executed text.
  2. Overwrite text_edit ONLY when the new incoming text differs from the
     last known upstream value (stored in node.__lbt_last_text).
  3. Emit text_edit's current value as the `text_edited` output via a
     hidden widget or direct node serialisation.
"""


class LBT_ShowTextEditable:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
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
        unique_id=None,
        extra_pnginfo=None,
    ):
        # ── Read text_edit from the saved workflow (widgets_values[1]) ────
        # text_edit is NOT declared in INPUT_TYPES so ComfyUI won't auto-render
        # a widget for it. The frontend creates it manually and serialises its
        # value into widgets_values[1]. We recover it here for the output.
        text_edit = text  # fallback: mirror upstream on first run

        workflow_node = None
        if unique_id is not None and extra_pnginfo is not None:
            if (
                isinstance(extra_pnginfo, list)
                and isinstance(extra_pnginfo[0], dict)
                and "workflow" in extra_pnginfo[0]
            ):
                workflow = extra_pnginfo[0]["workflow"]
                workflow_node = next(
                    (x for x in workflow["nodes"]
                     if str(x["id"]) == str(unique_id)),
                    None,
                )

        if workflow_node is not None:
            wv = workflow_node.get("widgets_values", [])
            # widgets_values layout (set by the frontend):
            #   [0] = last upstream text  (for change detection)
            #   [1] = text_edit content   (user-edited)
            if len(wv) >= 2:
                text_edit = wv[1]

            # Persist the updated last-upstream value back so the frontend
            # can detect changes correctly on the next load.
            workflow_node["widgets_values"] = [text, text_edit]

        # ── Send data back to the frontend for display update ─────────────
        return {
            "ui": {
                # Consumed by the frontend to refresh text_display and decide
                # whether to overwrite text_edit.
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
