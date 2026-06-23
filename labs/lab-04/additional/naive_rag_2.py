from functools import partial

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser, OutputFixingParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field



class Person(BaseModel):
    first_name: str = Field(description="Imię")
    last_name: str = Field(description="Nazwisko")
    position: str = Field(description="Stanowisko w firmie")

class ManagementBoard(BaseModel):
    members: list[Person] = Field(description="Lista członków zarządu")

load_dotenv()


loader = PyPDFLoader("ORLEN_250821_2025.pdf")

pages = loader.load()

documents = []

for page in pages:
    doc = Document(page_content=page.page_content, metadata=page.metadata)


print(f"Loaded {len(pages)} pages from the PDF document.")
print(pages[0].page_content)
print(pages[0].metadata)



splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=50)

split_docs = splitter.split_documents(pages)

embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large-instruct")
embeddings2 = OpenAIEmbeddings()


vectordb = Chroma.from_documents(documents=split_docs,
                                    embedding=embeddings,
                                 persist_directory="data/chroma_db_orlen"
                                 , collection_name="orlen_hf")

print(vectordb.search("Jaki jest skład zarządu i rady nadzorczej Orlen ?", search_type="similarity", k=2))

template = ("""
Odpowiedz na pytanie na podstawie kontekstu.

Kontekst: {kontekst}

Pytanie: {pytanie}

Zwróć odpowiedź w formacie JSON zgodnym z poniższą specyfikacją:
{format_instructions}

Upewnij się, że odpowiedź jest poprawnym JSON-em.
""")

parser = PydanticOutputParser(pydantic_object=ManagementBoard)

prompt = ChatPromptTemplate.from_template(template=template,partial_variables={"format_instructions": parser.get_format_instructions()})

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

retrieval = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 3})


chain = ({"kontekst": retrieval,"pytanie": RunnablePassthrough()}|
         prompt|
         llm|
         parser)

output = chain.invoke("Jaki jest skład zarządu i rady nadzorczej Orlen ?")
print(output)