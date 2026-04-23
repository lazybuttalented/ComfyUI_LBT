"""
Switch No Pause (LBT)

Reproduces the native Switch (CFG) node behavior with one key difference:
  - When boolean is True  → on_false side may be disconnected / errored / None
                            without interrupting the workflow.
  - When boolean is False → on_true  side may be disconnected / errored / None
                            without interrupting the workflow.

Implementation uses the classic ComfyUI INPUT_TYPES API with:
  * AlwaysEqualProxy  – allows the ports to accept ANY data type
  * {"lazy": True}    – tells the executor to skip evaluating the inactive branch
  * "optional"        – prevents the executor from requiring both inputs before execution
  * check_lazy_status – mirrors the native Switch node's lazy-evaluation logic
                        but gracefully handles the case where the inactive input
                        is absent/None/errored (no ExecutionBlocker, no exception).
"""


# ── type helper ──────────────────────────────────────────────────────────────
class _AnyType(str):
    """A string subclass that compares equal to every other string.
    Used as a wildcard type token so the port accepts any connection."""

    def __eq__(self, _other):
        return True

    def __ne__(self, _other):
        return False

    def __hash__(self):
        # str.__hash__ must stay consistent with __eq__; fix that here
        return hash("*")


any_type = _AnyType("*")


# ── node ─────────────────────────────────────────────────────────────────────
class LBT_SwitchNoPause:
    """
    Switch No Pause (LBT)
    ─────────────────────
    Boolean-controlled switch that never pauses the workflow when the
    *inactive* branch is missing, disconnected, or encountered an error.

    Ports
    ─────
    boolean  : BOOLEAN  – selector (True → on_true, False → on_false)
    on_true  : *        – value forwarded when boolean is True
    on_false : *        – value forwarded when boolean is False

    Output
    ──────
    output   : *        – the selected value, or None if that branch is absent
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                # Both branches are optional AND lazy so the executor
                # will not demand them before we decide which one is needed.
                "on_true":  (any_type, {"lazy": True}),
                "on_false": (any_type, {"lazy": True}),
            },
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    FUNCTION = "execute"
    CATEGORY = "LBT"

    # ── lazy-evaluation gate ──────────────────────────────────────────────────
    @classmethod
    def check_lazy_status(cls, boolean, on_true=None, on_false=None):
        """
        Mirror the native Switch node's check_lazy_status.

        Return a list of input names that still need to be evaluated,
        or an empty list / None when everything is ready.

        Key difference from the native node:
          If the *needed* input is absent (None because it was never
          connected or because its upstream node failed), we do NOT
          request it again – we let execute() handle the None gracefully
          instead of blocking the whole workflow.
        """
        if boolean:
            # We need on_true. Request it only if it hasn't been evaluated yet.
            if on_true is None:
                return ["on_true"]
        else:
            # We need on_false. Request it only if it hasn't been evaluated yet.
            if on_false is None:
                return ["on_false"]
        # Both branches already evaluated (or the needed one is ready) → proceed.
        return []

    # ── execution ─────────────────────────────────────────────────────────────
    def execute(self, boolean, on_true=None, on_false=None):
        """
        Return the active branch's value.

        If the active branch happens to be None (disconnected, upstream error,
        or deliberately empty), we return None rather than raising an exception
        – this keeps the workflow alive for any downstream nodes that can
        tolerate a None input.
        """
        result = on_true if boolean else on_false
        return (result,)


# ── registration ─────────────────────────────────────────────────────────────
NODE_CLASS_MAPPINGS = {
    "LBT_SwitchNoPause": LBT_SwitchNoPause,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_SwitchNoPause": "Switch No Pause (LBT)",
}
