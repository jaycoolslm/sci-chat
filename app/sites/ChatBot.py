import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from lib.chat_with_data import ChatWithData, VectorDBParams, ChatParams
import random, json
from langchain.document_loaders import DirectoryLoader, TextLoader, JSONLoader
from langchain.text_splitter import SpacyTextSplitter, NLTKTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.query_constructor.base import AttributeInfo

def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["journal"] = record["journal"]["title"]
    metadata["publisher"] = record["journal"]["publisher"]
    if "keywords" in record:
        metadata["keywords"] = "; ".join(record["keywords"])
    metadata["year"] = int(record["year"])
    metadata["author"] = "; ".join([author["name"] for author in record["author"]])

    metadata["url"] = record["link"][0]["url"]
    metadata["title"] = record["title"]
    return metadata

loader = JSONLoader(
    file_path="doaj/a.json",
    jq_schema=".[].bibjson",
    content_key="abstract",
    metadata_func=metadata_func,
)

metadata_field_info = [
    AttributeInfo(
        name="journal",
        type="string",
        description="Name of the journal the paper was published in.",
    ),
    AttributeInfo(
        name="publisher",
        type="string",
        description="Name of the publisher of the journal the paper was published in. Queries may not \
            include the exact name of the publisher, but should be similar.",
    ),
    AttributeInfo(
        name="keywords",
        type="string",
        description="List of keywords associated with the paper.",
    ),
    AttributeInfo(
        name="year",
        type="int",
        description="Year the paper was published.",
    ),
    AttributeInfo(
        name="author",
        type="string",
        description="List of authors of the paper.",
    ),
    AttributeInfo(
        name="url",
        type="string",
        description="URL of the paper.",
    ),
    AttributeInfo(
        name="title",
        type="string",
        description="Title of the paper.",
    ),
]

api_key = ""


llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=api_key)

def chatbot():

    if "vector_db_kwargs" not in st.session_state:
        st.session_state.vector_db_kwargs = {
            # which documents to load
            # "docs": DirectoryLoader(
            #     "./corpus", glob="**/body.txt", loader_cls=TextLoader, show_progress=True
            # ).load()[:100],
            "docs": JSONLoader(
                file_path="doaj/a.json",
                jq_schema=".[].bibjson",
                content_key="abstract",
                metadata_func=metadata_func,
            ).load()[:100],
            # which text splitter to use
            "splitter": NLTKTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100, 
                add_start_index=True
            ),
            "llm": llm,
            "document_content_description": "Abstract of a research paper.",
            "metadata_field_info": metadata_field_info,
            # which embedding function to use
            "embedding": HuggingFaceEmbeddings(
                model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
            ),
            # where to save the vector db
            "persist_directory": "./vectordb/metadata",
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
    if "chat_params_kwargs" not in st.session_state:
        st.session_state.chat_params_kwargs = {
            # which memory type to use
            "memory": ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            ),
            # which llm to use to generate questions
            "question_generator": LLMChain(
                llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=api_key),
                prompt=CONDENSE_QUESTION_PROMPT
            ),
            # which chain to use to combine retrieved documents
            "combine_docs_chain": load_qa_chain(
                ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=api_key),
                chain_type="stuff"
            ),
        }
    if "vector_db_params" not in st.session_state:
        st.session_state.vector_db_params = VectorDBParams(**st.session_state.vector_db_kwargs)
    if "chat_params" not in st.session_state:
        st.session_state.chat_params = ChatParams(**st.session_state.chat_params_kwargs)
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = ChatWithData(st.session_state.vector_db_params, st.session_state.chat_params)

    with st.sidebar:
        # retriever algorithm
        st.session_state.vector_db_kwargs["retriever_kwargs"]["search_type"] = st.radio(
            "Retriever Algorithm",
            ("similarity", "mmr"), # similarityatscore_threshold
            horizontal=True,
            format_func=lambda x: "Similarity" if x == "similarity" else "Maximum Marginal Relevance"
        )
        # fetch k for mmr
        if st.session_state.vector_db_kwargs["retriever_kwargs"]["search_type"] == "mmr":
            st.session_state.vector_db_kwargs["retriever_kwargs"]["search_kwargs"]["fetch_k"] = st.number_input(
                "Number of documents to fetch",
                min_value=1,
                max_value=30,
                value=5,
                step=1
            )
        # k for retriever
        st.session_state.vector_db_kwargs["retriever_kwargs"]["search_kwargs"]["k"] = st.number_input(
            "Number of documents to retrieve",
            min_value=1,
            max_value=10,
            value=2,
            step=1

        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "title_count" not in st.session_state:
        st.session_state.title_count = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Response output
    ## Function for taking user prompt as input followed by producing AI generated responses
    def generate_response(prompt):
        response, metadatas = st.session_state.chatbot.chat(prompt)
        markdown_str = f"{response}\n\n Check out these sources:\n\n"
        for metadata in metadatas:
            print("Metadata: ", json.dumps(metadata, indent=2))
            # handle addition of sources to markdown
            title = metadata["title"]
            url = metadata["url"]
            markdown_str += f"- [{title}]({url})\n"
            # handle data visulisation
            existing_title = next((title for title in st.session_state.title_count if title["title"] == metadata["title"]), None)
            if existing_title:
                existing_title["count"] += 1
            else:
                st.session_state.title_count.append({
                    "title": metadata["title"],
                    "count": 1
                })
        return markdown_str

    

    ## Conditional display of AI generated responses as a function of user provided prompts
    def get_random_phrase():
        phrases = [
            "Hmm... Give me a second!",
            "Just a moment, let me think...",
            "Hold on, I'm processing that...",
            "Let me ponder on that for a second...",
            "Hang tight, I'm considering your request...",
            "Wait a bit, I'm just figuring that out..."
        ]
        return random.choice(phrases)

    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner(get_random_phrase()):
            response = generate_response(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

       