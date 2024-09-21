import inspect
import logging
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

# Custom logging formatter
class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.INFO: Fore.GREEN,
        logging.ERROR: Fore.RED,
        logging.WARNING: Fore.YELLOW,
    }
    FILE_COLOR = Fore.CYAN + Style.BRIGHT
    MESSAGE_COLOR_BY_FILE = {}

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, Style.RESET_ALL)
        levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        filename_lineno = f"{self.FILE_COLOR}{record.filename}:{record.lineno:<5}{Style.RESET_ALL}"
        message_color = self.MESSAGE_COLOR_BY_FILE.get(record.filename, Style.RESET_ALL)
        colored_message = f"{message_color}{record.msg}{Style.RESET_ALL}"
        record.timestamp = datetime.now().isoformat()
        log_output = f"{levelname}:     {filename_lineno} - {colored_message}"
        return log_output

color_formatter = ColorFormatter('%(levelname)s: %(filename_lineno)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(color_formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)

# Map string color names to `colorama.Fore` attributes
COLOR_MAP = {
    "BLACK": Fore.BLACK,
    "RED": Fore.RED,
    "GREEN": Fore.GREEN,
    "YELLOW": Fore.YELLOW,
    "PURPLE": Fore.BLUE,
    "MAGENTA": Fore.MAGENTA,
    "CYAN": Fore.CYAN,
    "WHITE": Fore.WHITE,
    "RESET": Style.RESET_ALL
}

def set_files_message_color(color_name):
    """Sets the message color for the calling file."""
    frame = inspect.stack()[1]
    caller_filename = frame.filename.split('/')[-1]
    color = COLOR_MAP.get(color_name.upper(), Style.RESET_ALL)

    if color_formatter:
        current_color = color_formatter.MESSAGE_COLOR_BY_FILE.get(caller_filename, None)

        if current_color == color:
            return

        color_formatter.MESSAGE_COLOR_BY_FILE[caller_filename] = color
        logger.info(f"Set message color for {caller_filename} to {color_name.upper()}")
    else:
        logger.warning(f"Could not find a ColorFormatter attached to the logger")



