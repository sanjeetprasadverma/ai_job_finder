# from sentence_transformers import SentenceTransformer
from common.config import embedding_model
# import ollama
from ollama import Client


class Embedder:
    def __init__(self, model=embedding_model.trans_model):
        # self.model = SentenceTransformer(model)
        self.client = Client(host=embedding_model.model_host)
        self.model =embedding_model.ollama_model
        
    def embed(self, text):
        response = self.client.embed(
            model=self.model,
            input=text
        )
        # response = self.model.encode(text)
        return response.embeddings[0]
    # def encode(self, jobs):
    #     results =[]
    #     for job in jobs:
    #         results.append({
    #             self.jobid: job.get('id'),
    #             self.title: job.get('title'),
    #             self.embed: self.model.encode(job.get('description'))
    #         })
    #     return results
embedder =Embedder()

# id TEXT,
#                     title TEXT,
#                     embedding VECTOR(384) 