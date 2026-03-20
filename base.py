class BaseAgent():
    def __init__(self):
        self.model = None
    def generate(self,user_request):
        pass
    def generate_json(self,user_request,schema):
        pass
    def embed(self,query):
        pass
    def count_tokens(self,query):
        pass
    def info(self):
        pass
    def stream(self,user_request):
        pass
    def batch_generate(self,batch):
        pass
