from .postgresLoader import LoadPostgres
from .postgresStgLoadder import LoadSTGPostgres
from .pgvectorLoader import LoadVector

class Loader:
    def __init__(self):
        self.loadPostgres = LoadPostgres()
        self.stg_load = LoadSTGPostgres()
        self.vectorLoad = LoadVector()
    
    def load(self,jobs):
        return self.loadPostgres.load(jobs)
        
    def load_stg(self):
        return self.stg_load.load()
    
    def load_vectorload(self):
        return self.vectorLoad.load()
        

