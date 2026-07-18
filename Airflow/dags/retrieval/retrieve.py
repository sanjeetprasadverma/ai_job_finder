from .sources.adzuna import Adzuna

class Retrieve():
    def __init__(self):
        self.adzuna= Adzuna()
    def fetch(self):
        results = []
        results.append(self.adzuna.fetch())
        return results
    
retriever = Retrieve()