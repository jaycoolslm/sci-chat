from app.lib.chat_with_data import ChatWithData, VectorDBParams, ChatParams
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import SpacyTextSplitter, NLTKTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.question_answering import load_qa_chain
import re

api_key = "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"

vector_db_kwargs = {
    # which documents to load
    "docs": DirectoryLoader(
        "./corpus", glob="**/abstract.txt", loader_cls=TextLoader, show_progress=True
    ).load(),
    # which text splitter to use
    "splitter": NLTKTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100, 
        add_start_index=True
    ),
    # which embedding function to use
    "embedding": HuggingFaceEmbeddings(
        model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
    ),
    # where to save the vector db
    "persist_directory": "./vectordb/chroma_test",
    # which vector db to use
    "vector_db": Chroma,
    # which retriever algorithms and parameters to use
    "retriever_kwargs": {
        "search_type": "mmr",
        "search_kwargs": {
            "fetch_k": 5,
            "k": 2
        }
    }
}

def remove_extra_whitespace_in_parentheses(text):
    def replace(match):
        # Replace multiple spaces with a single space
        return re.sub(r"\s+", " ", match.group())

    return re.sub(r"\(.*?\)", replace, text)

def basic_preprocessing(doc):
    # remove whitespace
    doc.page_content = doc.page_content.replace("\n", " ")
    doc.page_content = doc.page_content.replace("\xa0", " ")
    doc.page_content = doc.page_content.strip()
    doc.page_content = remove_extra_whitespace_in_parentheses(doc.page_content)
    return doc

chunked_docs = vector_db_kwargs["splitter"].split_documents(
    [basic_preprocessing(doc) for doc in vector_db_kwargs["docs"]]
)

chunked_docs[0]['metadata'] = {"title": "test"}

print(chunked_docs[0])

# chat_params_kwargs = {
#     # which memory type to use
#     "memory": ConversationBufferMemory(
#         memory_key="chat_history",
#         return_messages=True
#     ),
#     # which llm to use to generate questions
#     "question_generator": LLMChain(
#         llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=api_key),
#         prompt=CONDENSE_QUESTION_PROMPT
#     ),
#     # which chain to use to combine retrieved documents
#     "combine_docs_chain": load_qa_chain(
#         ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=api_key),
#         chain_type="stuff"
#     ),
# }

# vector_db_params = VectorDBParams(**vector_db_kwargs)

# chat_params = ChatParams(**chat_params_kwargs)

# chatbot = ChatWithData(vector_db_params, chat_params)


# while(True):
#     question = input("User: ")
#     print("Bot: " + chatbot.chat(question))