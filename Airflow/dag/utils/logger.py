import logging
import sys

logging.basicConfig(
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ],
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# def global_exception_handler(exc_type, exc_value, exc_traceback):
#     # Don't log KeyboardInterrupt as an error
#     if issubclass(exc_type, KeyboardInterrupt):
#         sys.__excepthook__(exc_type, exc_value, exc_traceback)
#         return

#     logger.exception(
#         "Unhandled exception",
#         exc_info=(exc_type, exc_value, exc_traceback),
#     )


# sys.excepthook = global_exception_handler