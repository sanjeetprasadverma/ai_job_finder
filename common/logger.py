import logging
import sys

class Loger:
    def __init__(
        self, 
        log_file ='app.log',
        logger_name='app',
        level=logging.INFO,
        ):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)
        
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Create log directory if needed
        # Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s"
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    #     logging.basicConfig(
    #     handlers=[
    #         logging.FileHandler('app.log'),
    #         logging.StreamHandler()
    #     ],
    #     level=logging.INFO,
    #     format="%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s",
    # )
    def get_logger(self):
        return self.logger
    
    
logger = Loger(
    logger_name='common',
    log_file='logs/common.log',
    level=logging.INFO
).get_logger()

airflow_logger = Loger(
    logger_name='airflow',
    log_file='logs/airflow.log',
    level=logging.INFO
).get_logger()

backend_logger = Loger(
    logger_name='backend',
    log_file='logs/backend.log',
    level=logging.INFO
).get_logger()

