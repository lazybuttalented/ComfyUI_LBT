class LBT_BooleanAND:
    """
    Boolean AND node.
    bool_1 ~ bool_32 are pre-declared as hidden inputs (forceInput).
    JS manages which sockets are actually visible by filtering node.inputs.
    input_count controls both JS display and backend evaluation range (2-32).
    Unconnected sockets within [1, input_count] default to True.
    """

    MAX_INPUTS = 32

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_count": ("INT", {"default": 2, "min": 2, "max": 32, "step": 1}),
            },
            "hidden": {
                f"bool_{i}": ("BOOLEAN", {"forceInput": True})
                for i in range(1, s.MAX_INPUTS + 1)
            },
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("result",)
    FUNCTION = "boolean_and"
    CATEGORY = "LBT"

    def boolean_and(self, input_count, **kwargs):
        result = True
        for i in range(1, input_count + 1):
            val = kwargs.get(f"bool_{i}", True)
            if not val:
                result = False
                break
        return (result,)


NODE_CLASS_MAPPINGS = {
    "LBT_BooleanAND": LBT_BooleanAND,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_BooleanAND": "Boolean AND (LBT)",
}
