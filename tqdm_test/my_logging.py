import logging
import datetime
import tqdm

from config import config_dict, IS_SETUP_DONE


def setup_logging(log_prefix, force_debug_level=logging.DEBUG):

    root = logging.getLogger()
    root.setLevel(force_debug_level)

    if config_dict[IS_SETUP_DONE]:
        pass
    else:
        __log_file_name = "{}-{}_log_file.txt".format(log_prefix,
                                                      datetime.datetime.utcnow().isoformat().replace(":", "-"))

        __log_format = '%(asctime)s - %(name)-30s - %(levelname)s - %(message)s'
        __console_date_format = '%Y-%m-%d %H:%M:%S'
        __file_date_format = '%Y-%m-%d %H-%M-%S'

        console_formatter = logging.Formatter(__log_format, __console_date_format)

        file_formatter = logging.Formatter(__log_format, __file_date_format)
        file_handler = logging.FileHandler(__log_file_name, mode='a', delay=True)

        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        root.addHandler(file_handler)

        tqdm_handler = TqdmLoggingHandler()
        tqdm_handler.setLevel(logging.DEBUG)
        tqdm_handler.setFormatter(console_formatter)
        root.addHandler(tqdm_handler)

        config_dict[IS_SETUP_DONE] = True


class TqdmLoggingHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        tqdm.tqdm.write(msg)
        self.flush()