from .sources.adzuna import Adzuna
from utils.logger import logger

class Retrieve():
    def __init__(self):
        self.adzuna= Adzuna()
    def fetch(self):
        results = []
        results.append(self.adzuna.fetch())
        logger.info("adzuna retriving completed")
        return results
    
retriever = Retrieve()