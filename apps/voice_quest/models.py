from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_community.vectorstores import Chroma
from operator import itemgetter
import numpy as np

from dotenv import load_dotenv
load_dotenv()

class QuestLLM:
    def __init__(self, prompt_path, output_parser, db_params):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)
        self.prompt_path = prompt_path
        self.output_parser = output_parser
        self.vector_db = Chroma(**db_params)
        self._template = self._get_template()

    def _make_retriever(self, query):
        retriever = self.vector_db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 2, "filter": {"keyword": query}}
        )
        return retriever
    
    def _cosine_similarity(self, vec1, vec2):
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    def _get_template(self):
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _set_prompt(self):
        return ChatPromptTemplate.from_template(self._template)

    def _make_chain(self, retriever):
        pass

    def invoke(self, **inputs):
        pass

class Quiz(QuestLLM):
    def __init__(self, prompt_path, output_parser, db_params):
        super().__init__(prompt_path, output_parser, db_params)

    def _make_chain(self, retriever):
        chain = (
            {
                "context": itemgetter("answer") | retriever,
                "answer": itemgetter("answer"),
            }
            | self._set_prompt()
            | self.llm
            | self.output_parser
        )
        return chain

    def invoke(self, answer):
        retriever = self._make_retriever(answer)
        chain = self._make_chain(retriever)
        return chain.invoke({"answer": answer})

class Hint(QuestLLM):
    def __init__(self, prompt_path, output_parser, db_params):
        super().__init__(prompt_path, output_parser, db_params)
        self.chat_history = []

    def _make_chain(self, retriever):
        chain = (
            {
                "context": itemgetter("user_word") | retriever,
                "user_word": itemgetter("user_word"),
                "answer": itemgetter("answer"),
                "chat_history": itemgetter("chat_history"),
            }
            | self._set_prompt()
            | self.llm
            | self.output_parser
        )
        return chain

    def invoke(self, user_word, answer):

        similarity = self._cosine_similarity(user_word, answer)
        retriever = self._make_retriever(user_word)
        chain = self._make_chain(retriever)
        response = chain.invoke({
                    "user_word": user_word,
                    "answer": answer,
                    "chat_history": self.chat_history
                })
        self.chat_history.append(f"User : {user_word}, Mom : {response}")
        return {
            "response" : response,
            "similarity" :  similarity
        }
    
###TestCode
