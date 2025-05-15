from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings
from models.llm_base import QuestLLM
from operator import itemgetter
import re

class Quiz(QuestLLM):
    '''트리거 시작하면 퀴즈를 내는 LLM'''
    def __init__(self, prompt_path, db_params, answer):
        super().__init__(prompt_path, db_params, answer)
        self.chain = self._make_chain()

    def _make_chain(self):
        chain = (
            {
                "context": itemgetter("answer") | self.retriever,
                "answer": itemgetter("answer"),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

    def start_quiz(self):
        response = self.chain.invoke({"answer": self.answer})
        response = re.sub(r"[^가-힣a-zA-Z0-9\s.,!?]", "", response)
        return response