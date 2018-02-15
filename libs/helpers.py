
class Color():
    _RED = "\033[1;31m"
    _BLUE = "\033[1;34m"
    _YELLOW = "\033[1;93m"
    _CYAN = "\033[1;36xm"
    _GREEN = "\033[0;32m"
    _RESET = "\033[0;0m"
    _BOLD = "\033[;1m"
    _REVERSE = "\033[;7m"

    @staticmethod
    def red(str):
        return Color.build(str, Color._RED)

    @staticmethod
    def green(str):
        return Color.build(str, Color._GREEN)

    @staticmethod
    def yellow(str):
        return Color.build(str, Color._YELLOW)

    @staticmethod
    def build(str, COLOR):
        return "%s%s%s" % (COLOR, str, Color._RESET)
