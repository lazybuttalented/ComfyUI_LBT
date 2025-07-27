
class LBT_ListInfo:
    """
    A node that takes an LBTlist and outputs its size (integer) and the list itself.
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "lbt_list": ("LBTlist",),
            }
        }

    RETURN_TYPES = ("INT", "LBTlist",)
    RETURN_NAMES = ("count", "lbt_list",)
    FUNCTION = "get_info"
    CATEGORY = "LBT"

    def get_info(self, lbt_list):
        count = len(lbt_list)
        return (count, lbt_list)

NODE_CLASS_MAPPINGS = {
    "LBT_ListInfo": LBT_ListInfo
}
