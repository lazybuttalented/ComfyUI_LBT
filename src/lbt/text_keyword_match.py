class LBT_TextKeywordMatch:
    """
    Text Keyword Match node.
    Checks whether any of the given keywords appear in the input text.
    Returns True if at least one keyword is found, otherwise False.

    Keywords are separated by commas (e.g. "cat, dog, bird").
    Matching is case-insensitive by default.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "keywords": ("STRING", {
                    "multiline": False,
                    "default": "keyword1, keyword2",
                    "tooltip": "Comma-separated list of keywords to search for.",
                }),
                "case_sensitive": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("matched",)
    FUNCTION = "match_keywords"
    CATEGORY = "LBT"

    def match_keywords(self, text, keywords, case_sensitive=False):
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        if not keyword_list:
            return (False,)

        compare_text = text if case_sensitive else text.lower()
        for kw in keyword_list:
            compare_kw = kw if case_sensitive else kw.lower()
            if compare_kw in compare_text:
                return (True,)

        return (False,)


NODE_CLASS_MAPPINGS = {
    "LBT_TextKeywordMatch": LBT_TextKeywordMatch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LBT_TextKeywordMatch": "Text Keyword Match (LBT)",
}
