
class LBT_StringToList:
    """
    A node that converts a formatted string into a list of strings (LBTlist).
    The input string must be in the format: "count, item1, item2, ...",
    where 'count' is an integer specifying the number of items.
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": False, "default": "1, item_name"}),
            }
        }

    RETURN_TYPES = ("LBTlist",)
    FUNCTION = "convert"
    CATEGORY = "LBT"

    def convert(self, text):
        parts = [p.strip() for p in text.split(',')]
        
        if len(parts) < 1:
            raise ValueError("Input string is empty or invalid.")

        try:
            count = int(parts[0])
        except ValueError:
            raise ValueError(f"Invalid count: The first element '{parts[0]}' must be an integer.")

        names = parts[1:]

        if len(names) != count:
            raise ValueError(f"Mismatch between specified count ({count}) and actual number of items ({len(names)}).")
        
        return (names,)

NODE_CLASS_MAPPINGS = {
    "LBT_StringToList": LBT_StringToList
}
