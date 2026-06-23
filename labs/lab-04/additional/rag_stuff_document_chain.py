from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

loader = PyPDFLoader("labs/lab-04/additional/ORLEN_250821_2025.pdf")

pages = loader.load()

print(f"Loaded {len(pages)} pages from the PDF document.")

documents = []

for page in pages[:10]:
    classification = llm.invoke("Classify the following text into one of the categories. Give only classification without explanation: "
                                                            "'Financial', 'Operational', 'Strategic', 'Regulatory', 'Market Analysis', "
                                                            "'Corporate Governance'. Text: " + page.page_content)
    print(classification.content)
    page.metadata['classification'] = classification.content
    doc = Document(page_content=page.page_content, metadata=page.metadata)
    print(doc.metadata)
    documents.append(doc.metadata)

    print(f"Loaded documents from the PDF document.")


splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=50,strip_whitespace=True)

embeddings = OpenAIEmbeddings()

document_splits = splitter.split_documents(pages)

vectordb = Chroma.from_documents(documents=document_splits,
                                    embedding=embeddings,
                                    collection_name="orlen2",
                                    persist_directory="data/chroma_db_orlen2")

retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 3})


system_prompt= """
You are an expert financial analyst. Use following context to answer the question.
Context: {context}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("user", "{input}"),
    ]
)

document_chain = create_stuff_documents_chain(llm,prompt)


retriever_db = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 3})

rag_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=document_chain)
output = rag_chain.invoke({"input":"Jaki jest skład zarządu i rady nadzorczej Orlen ?"})
print(output)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

chain = ({"context":retriever_db|format_docs,"input": RunnablePassthrough()}
         |prompt
         |llm
         |StrOutputParser()
         )

output = chain.invoke("Jaki jest skład zarządu i rady nadzorczej Orlen ?")
print("DWA")
print(output)