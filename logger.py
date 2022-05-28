from datetime import datetime
import os


class Logger:
    """
    Logger class with three levels of logging namely INFO, DEBUG, EXCEPTION and two
    modes of writing log namely command line and external file logging
    """

    # Static variables
    # right-padding
    PADDING = 9
    # current directory
    CURR_DIRECTORY = os.getcwd()

    def __init__(self, filename=None, mode="console"):
        """
        Parametrized Contructor
        @params
        filename = name of the file
        mode = console/file
        """
        # If no file name is provided make a default one
        if filename is None:
            today = datetime.now().today()
            # making the file name unique
            self.filename = f"log[{today}].log"
        else:
            self.filename = filename
        # Default logging mode is console
        self.mode = mode
        # append subdirectory to filename
        # if log folder doesnot exists in current directory make one
        path = self.CURR_DIRECTORY + "/log"
        if not os.path.isdir(path):
            os.mkdir(path)
        # append path
        self.filename = path + "/" + self.filename

    def clear(self):
        """Clears the log file"""
        if self.mode == "file":
            with open(self.filename, "r+") as file:
                file.truncate(0)
        else:
            os.system("cls" if os.name in ("nt", "dos") else "clear")

    def log(self, msg, level="INFO"):
        """
        Functions log message with specified level
        @params
        msg = message to be displayed
        level = log level [INFO, DEBUG, ERROR]
        """
        log_type = level.ljust(self.PADDING)
        now = datetime.now().today()
        log_message = f"{log_type}|{now.hour}:{now.minute}| {msg}\n"
        if self.mode == "file":
            try:
                with open(self.filename, "a") as file:
                    file.write(log_message)
            except Exception as e:
                print(f"An error has occured while logging: {e}")
        else:
            print(log_message)

    def info(self, msg):
        """
        Log info
        @params
        msg = info message to be displayed
        """
        self.log(msg, "INFO")

    def debug(self, msg):
        """
        Log Debug
        @params
        msg = debug message to be displayed
        """
        self.log(msg, "DEBUG")

    def error(self, msg):
        """
        Log Exception
        @params
        msg = error message to be displayed
        """
        self.log(msg, "ERROR")


# Creating logger instance
logger = Logger(mode="file")
