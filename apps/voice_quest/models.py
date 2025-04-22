from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import OpenAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

class QuizLLM:
    '''LLM 모델 생성 클래스'''
    def __init__(self, prompt_path):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)
        self.prompt_path = prompt_path
        self.memory = ConversationBufferMemory(llm=self.llm, return_messages=True)
        self.chain = self._make_chain()

    def _make_chain(self):
        pass

    def _get_template(self):
        with open(self.prompt_path, "r") as f:
            return f.read()
        
    def _set_prompt(self, **inputs):
        pass

    def invoke(self, inputs):
        prompt = self._set_prompt(inputs)
        response = self.chain.invoke(prompt)

        return response
    
    