from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import re

loader = PyMuPDFLoader("./data/PDF/Epilogue.pdf")
docs = loader.load()

def preprocess(text):
    new_text = text.replace("Document", "")
    return new_text

for i in range(3):
    docs[i].page_content = preprocess(docs[i].page_content)

def split_with_bracket_keyword(documents):
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

# keyword 기준으로 먼저 쪼개
split_docs = split_with_bracket_keyword(docs)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n", " "] 
)

chunks = splitter.split_documents(split_docs)

# Vector DB에 저장 코드
embedding = OpenAIEmbeddings()
vector_db = Chroma.from_documents(documents=chunks, embedding=embedding, persist_directory="./data/chroma_db", collection_name="openai")
vector_db.persist()