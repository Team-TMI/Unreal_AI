from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

class QuestLLM:
    def __init__(self, prompt_path, db_params, answer):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)
        self.prompt_path = prompt_path
        self.answer = answer
        self.vector_db = Chroma(**db_params)
        self.prompt = self._set_prompt()
        self.retriever = self._make_retriever()

    def _make_retriever(self):
        retriever = self.vector_db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 2, "filter": {"keyword": self.answer}}
        )
        return retriever

    def _get_template(self):
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _set_prompt(self):
        return ChatPromptTemplate.from_template(self._get_template())

    def _make_chain(self):
        pass