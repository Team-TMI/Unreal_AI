from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()

import re

def preprocess(text):
    """텍스트 전처리 함수."""
    return text.replace("Document", "")

def split_with_bracket_keyword(documents):
    """[keyword]\n 기준으로 문서 분할."""
    result = []
    pattern = r"\[(.*?)\]\n"

    for doc in documents:
        text = doc.page_content
        matches = list(re.finditer(pattern, text))

        for i, match in enumerate(matches):
            keyword = match.group(1)
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chunk_text = text[start:end].strip()

            if chunk_text:
                result.append(
                    Document(
                        page_content=chunk_text,
                        metadata={**doc.metadata, "keyword": keyword}
                    )
                )
    return result

if __name__ == "__main__":
    # PDF 로드
    loader = PyMuPDFLoader("./data/PDF/Epilogue.pdf")
    docs = loader.load()

    # 전처리
    for i in range(len(docs)):
        docs[i].page_content = preprocess(docs[i].page_content)

    # [keyword] 기준으로 쪼개기
    split_docs = split_with_bracket_keyword(docs)

    # chunk 나누기
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n", " "]
    )
    chunks = splitter.split_documents(split_docs)

    # Vector DB 저장
    embedding = OpenAIEmbeddings()
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory="./data/chroma_db",
        collection_name="openai"
    )
    vector_db.persist()

    print("벡터 db 저장 완료료")