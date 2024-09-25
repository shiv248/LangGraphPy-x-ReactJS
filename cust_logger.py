import inspect
import logging
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)  # Automatically reset color formatting after each log
                      # Allowing different logs to have different colors

# Custom logging formatter to add colors and formatting based on log level
class ColorFormatter(logging.Formatter):
    # checkout Colorama's available Fore (colors) and Styles https://github.com/tartley/colorama

    COLORS = {
        logging.INFO: Fore.GREEN,
        logging.ERROR: Fore.RED,
        logging.WARNING: Fore.YELLOW
    }
    FILE_COLOR = Fore.CYAN + Style.BRIGHT  # Filename and line number in bright cyan
    MESSAGE_COLOR_BY_FILE = {}  # Custom color per file, which gets added to by helper function

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, Style.RESET_ALL) # Style.RESET_ALL resets foreground, background, and brightness.
        levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        filename_lineno = f"{self.FILE_COLOR}{record.filename}:{record.lineno:<5}{Style.RESET_ALL}" # <{#} is num spacing
        message_color = self.MESSAGE_COLOR_BY_FILE.get(record.filename, Style.RESET_ALL)
        colored_message = f"{message_color}{record.msg}{Style.RESET_ALL}"
        record.timestamp = datetime.now().isoformat()  # Add timestamp to logs
        log_output = f"{levelname}:     {filename_lineno} - {colored_message}"
        return log_output

color_formatter = ColorFormatter('%(levelname)s: %(filename_lineno)s - %(message)s')
handler = logging.StreamHandler()  # Console logging handler
handler.setFormatter(color_formatter)  # Set our handler to our custom formatter above
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set our logger level to INFO
logger.addHandler(handler)

# Set logging level for external libraries to reduce clutter in terminal view
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
    """Sets the message color for the calling file based on the provided color name."""
    frame = inspect.stack()[1]  # Get the function caller's stack frame (name)
    caller_filename = frame.filename.split('/')[-1]  # Extract the filename
    color = COLOR_MAP.get(color_name.upper(), Style.RESET_ALL)  # Get color from COLOR_MAP if it exists otherwise default white

    if color_formatter:
        current_color = color_formatter.MESSAGE_COLOR_BY_FILE.get(caller_filename, None)

        if current_color == color:  # Avoid redundant color setting
            return

        color_formatter.MESSAGE_COLOR_BY_FILE[caller_filename] = color
        logger.info(f"Set message color for {caller_filename} to {color_name.upper()}")  # Log the file color set to change
    else:
        # edge case if the color formatter wasn't setup properly
        logger.warning(f"Could not find a ColorFormatter attached to the logger")
