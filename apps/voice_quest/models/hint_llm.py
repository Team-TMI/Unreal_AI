from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.schema.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings
from operator import itemgetter
from models.llm_base import QuestLLM
import numpy as np


class Hint(QuestLLM):
    def __init__(self, prompt_path, db_params, answer):
        super().__init__(prompt_path, db_params, answer)
        self.history_store = {}
        self.chain = self._make_chain()

    def get_session_history(self, session_id):
        if session_id not in self.history_store:
            self.history_store[session_id] = ChatMessageHistory()
        return self.history_store[session_id]

    def _make_chain(self):
        chain = (
            {
                "context": lambda x: self.retriever.invoke(x["user_word"].content),
                "user_word": itemgetter("user_word"),   
                "answer": itemgetter("answer"),
                "chat_history": itemgetter("chat_history"),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        return RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="user_word",
            history_messages_key="chat_history",
        )

    def similarity(self, user_word):
        """user_word와 self.answer의 유사도(float)만 리턴"""
        embedding_model = OpenAIEmbeddings()
        user_vec = np.array(embedding_model.embed_query(user_word))
        answer_vec = np.array(embedding_model.embed_query(self.answer))

        similarity = np.dot(user_vec, answer_vec) / (np.linalg.norm(user_vec) * np.linalg.norm(answer_vec))
        return similarity
    
    def invoke(self, user_word, session_id="default"):
        response = self.chain.invoke(
            {
                "user_word": HumanMessage(content=user_word),
                "answer": self.answer
            },
            config={"configurable": {"session_id": session_id}}
        )
        print(f"[힌트] : {response}")
        similarity = self.similarity(user_word)
        return {
            "response" : response,
            "similarity" : similarity
        }