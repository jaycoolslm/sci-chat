import streamlit as st
from streamlit_option_menu import option_menu
from sites.Corpus import corpus
from sites.ChatBot import chatbot
from sites.Analytics import analytics


st.set_page_config(page_title="SciChat - An LLM-powered Research Assistant")

if "active_page" not in st.session_state:
    st.session_state.active_page = "ChatBot"

# if "runpage" not in st.session_state:
#     st.session_state.runpage = corpus

# 1. as sidebar menu
with st.sidebar:
    st.session_state.active_page = option_menu("SciChat", ["Corpus", 'ChatBot', 'Analytics'], 
        icons=['archive', 'chat-left-text', 'bar-chart'], menu_icon="infinity", default_index=0)

        

if st.session_state.active_page == "Corpus":
    corpus()
elif st.session_state.active_page == "ChatBot":
    chatbot()
elif st.session_state.active_page == "Analytics":
    analytics()

# st.session_state.runpage()
