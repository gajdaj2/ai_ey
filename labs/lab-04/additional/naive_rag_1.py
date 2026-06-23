from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

loader = PyPDFLoader("labs/lab-04/additional/OWU_i_Karta_produktu_Warta_Dla_Ciebie_i_Rodziny_od_14.04.2024.pdf")

load_dotenv()

pages = loader.load()


print(f"Loaded {len(pages)} pages from the PDF document.")
print(pages[1].page_content)

docs = []

for doc in pages:
    print(doc.metadata)
    print("-----")
    docs.append(Document(page_content=doc.page_content, metadata=doc.metadata))


splitter = CharacterTextSplitter(chunk_size=1024, chunk_overlap=50)

documents_split = splitter.split_documents(docs)
print(f"Split into {len(documents_split)} chunks.")

embeddings = OpenAIEmbeddings()

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

vectordb = Chroma.from_documents(documents=documents_split,embedding=embeddings,collection_name="owu_openai")

print(vectordb.search("Jaka jest karencja na zgon członka rodziny?", search_type="similarity", k=2))

template = ("""
Odpowiedz na pytanie na podstawie kontekstu.

Kontekst: {kontekst}

Pytanie: {pytanie}


Upewnij się, że odpowiedź jest poprawnym JSON-em.
""")

prompt = PromptTemplate.from_template(template=template)
retrieval = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 3})

chain = ({"kontekst": retrieval,"pytanie": RunnablePassthrough()}|prompt|llm|StrOutputParser())

output = chain.invoke("Ile mam czasu na rozwiazanie umowy ?")
print(output)