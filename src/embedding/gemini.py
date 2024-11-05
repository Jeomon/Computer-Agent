from requests import RequestException,HTTPError,ConnectionError
from src.embedding import BaseEmbedding
from httpx import Client
from typing import Literal

class GeminiEmbedding(BaseEmbedding):
    def __init__(self,model:str='',output_dimensionality:int=None,task_type:Literal['TASK_TYPE_UNSPECIFIED','RETRIEVAL_QUERY','RETRIEVAL_DOCUMENT','SEMANTIC_SIMILARITY','CLASSIFICATION','CLUSTERING']='',api_key:str='',base_url:str=''):
        self.api_key=api_key
        self.model=model
        self.base_url=base_url
        self.output_dimensionality=output_dimensionality
        self.task_type=task_type
        self.headers={'Content-Type': 'application/json'}
    def embed(self,text:str='',title:str=''):
        url=self.base_url or f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:embedContent"
        headers=self.headers
        params={'key':self.api_key}
        payload={
            'model':f'models/{self.model}',
            'content':{
                'parts':[
                    {
                        'text':text
                    }
                ]
            }
        }
        if self.task_type:
            payload['task_type']=self.task_type
        if self.output_dimensionality:
            payload['output_dimensionality']=self.output_dimensionality
        if title:
            payload['title']=title
        try:
            with Client() as client:
                response=client.post(url=url,json=payload,headers=headers,params=params)
            response.raise_for_status()
            return response.json()['embedding']['values']
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)