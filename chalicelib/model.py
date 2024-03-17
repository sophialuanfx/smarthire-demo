
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain import hub


apiKey="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"

def resumeSum(userName, resumePath):
    
    #loader =PyPDFLoader(f"./data/{resumePath}")
    loader =PyPDFLoader(resumePath)
    #loader =PyPDFLoader(f"./{resumePath}")

    
    pages = loader.load_and_split()
    
    #os.environ['OPENAI_API_KEY'] = getpass.getpass('OpenAI API Key:')
    faiss_index = FAISS.from_documents(pages, OpenAIEmbeddings(openai_api_key=apiKey))
    retriever = faiss_index.as_retriever()

    #prompt = ChatPromptTemplate.from_template(template)
    
    prompt = hub.pull("rlm/rag-prompt")
    model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=apiKey)

    def format_docs(docs):
            return "\n\n".join([d.page_content for d in docs])
        
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    solution=chain.invoke(
            f"""
            Structure {userName} background by filling in the section below
            - Best Matching Job Positions (for example "Data Engineer", "Product Manager", etc) rank tron best fit to less fit:
            - Top Skills he/she has (10 to 20):
            - Industries (tike Retail, Tech, Consulting, Government, Finance, etc.):
            - Years of Experience (estimate if not specified, e.g 3 YOE, 5+ YOE):
            - Location (City, Country):
            - Open to Relocate (Yes/No):
            - Full Experience (including everything):
            """)

    #print(f"This is resume and Match func: {solution}")
    return solution

def resuemJobMatch(resume_summary, job_path):
    #loader = CSVLoader(file_path=job_path)
    loader = CSVLoader(file_path="./data/raw_google_1129.csv", encoding = "utf-8")

    pages = loader.load_and_split()
    faiss_index = FAISS.from_documents(pages, OpenAIEmbeddings(openai_api_key=apiKey))
    jobs_retriever = faiss_index.as_retriever()

    prompt = hub.pull("rlm/rag-prompt")
    model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=apiKey)

    def format_docs(docs):
            return "\n\n".join([d.page_content for d in docs])

    chain = (
        {"context": jobs_retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    solution=chain.invoke(
        f"""
        Given the resume in {resume_summary}
        Pick the recommend the top 5 matched jobs for the data with run time 2023-11-27, return applyLinks
        """)

        
    #print(f"This is resume and Match func: {solution}")
    return solution

    

