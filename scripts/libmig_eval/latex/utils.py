def to_upper_camel_case(text: str):
    """convert a space separated string to upper camel case"""
    if not text:
        return ""

    upper_words = [word[0].capitalize() + word[1:] for word in text.split()]
    return "".join(upper_words)


def to_macro_name(text: str):
    """Converts a given text to a valid latex macro name. Does the followings:
    1. Prepend with backslash (\)
    2. Converts to camel case using words separated by space or underscore
    Example: 'alpha beta_gamma' -> '\AlphaBetaGamma'
    """

    text = text.replace("_", " ").replace("-", " ")
    texts = text.split()

    macro_name = "".join(to_upper_camel_case(text) for text in texts)
    if macro_name[0] != "\\":
        macro_name = "\\" + macro_name
    return macro_name


def escape(text: str):
    """escape a text to be usable as latex text"""
    return text.replace("%", "\\%")


def format_int(val: any):
    # format with commas for thousands, millions, etc.
    val = int(round(val, 0))
    return "{:,}".format(val)


def try_format_int(val: any):
    try:
        val = round(val, 0)
    except TypeError:
        pass

    if not isinstance(val, int):
        return val
    return format_int(val)


def red(content: str):
    return "\\red{" + content + "}"
