from .postgresLoader import LoadPostgres
from .postgresStgLoadder import LoadSTGPostgres

class Loader:
    def __init__(self):
        self.loadPostgres = LoadPostgres()
        self.stg_load = LoadSTGPostgres()
    
    def load(self,jobs):
        self.loadPostgres.load(jobs)
        
    def load_stg(self):
        self.stg_load.load()
        

