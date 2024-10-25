import argparse
import os
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from verifiers import check_hallucination, check_answer
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

TAVILY_API = os.getenv('tavily_API')
BASE_URL = os.getenv('base_URL')
embeddings = OllamaEmbeddings(model="nomic-embed-text:latest",
                                  base_url=BASE_URL)

tavily_client = TavilyClient(api_key=TAVILY_API)



CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context. If the answer to the question is not in the context, simply respond with
"I don't know":

{context}

---

Answer the question based ONLY on the above context. If the answer to the question is not in the context, simply respond with
"I don't know": {question}
"""


def main(): #run in CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    parser.add_argument('-ol',type=bool,help='turns on online query',)
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text,)

def run_chatbot(Query,ext_search=False): # Run in Streamlit
    return query_rag(Query,ext_search)
    


def query_rag(query_text: str,ext_search:bool=False):
    # Prepare the DB.
    embedding_function = embeddings
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    model = OllamaLLM(model="Llama3.1",
                      base_url= BASE_URL)
    response_text = model.invoke(prompt)
    if ext_search:#looking up online resources must be enabled manually
        check = check_answer(question=query_text,generation=response_text) #verifying answer is coming from prompt
        if check['score'] == 'no' :
            new_context = tavily_client.get_search_context(query=query_text)
            new_prompt = prompt_template.format(context=new_context, question=query_text)
            response_text = model.invoke(new_prompt)
            new_response = f'***THIS INFORMATION WAS RETREIVED ONLINE***\n\nResponse:{response_text}'
            return new_response

    # This will run if check['score'] is True or ext_search is False
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\n\nSources: {sources}"
    print(formatted_response)
    return formatted_response


if __name__ == "__main__":
    main()