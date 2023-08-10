import streamlit as st
from lib.scrape import ScienceDirect
import os
from .ChatBot import chatbot

def corpus():

    if "sd" not in st.session_state:
        st.session_state.sd = ScienceDirect(
            api_key="cb941e863e2c5dcdd18ef5d262f8c9bd",
        )

    if "num_displayed" not in st.session_state:
        st.session_state.num_displayed = 5  # Initialize the number of displayed papers

    if "papers" not in st.session_state:
        st.session_state.papers = []  # Initialize the number of displayed papers

    with st.sidebar:
        st.title("🧪💬 SciChat App")
        st.markdown(
            """
            ## About
            This app is chatbot for your research papers
            """
        )
        st.write("Made with ❤️  by Jay Cool")

    # Function for the first page
    st.header("Research Query")
    query = st.text_input("Enter your research query here:")
    offset = st.slider('How many papers do you want to scrape? (fewer = quicker)', 0, 6100, 100, 100)

    # function to create markdown cards
    def create_card(authors, publication_date, title, uri):
        card = f"""
        **Title:** {title}<br>
        **Authors:** {", ".join([author["name"] for author in authors])} <br>
        **Publication Date:** {publication_date} <br>
        **Link:** [Read More]({uri})
        """
        return card

    
    def display_papers():
        print("Papers to display: ", st.session_state.num_displayed)
        for i in range(st.session_state.num_displayed):
            paper = st.session_state.papers[i]
            st.write("---")
            st.markdown(create_card(paper["authors"], paper["publicationDate"], paper["title"], paper["uri"]), unsafe_allow_html=True)

    if st.button("Enter", disabled=False if query else True) or query:
        st.session_state.num_displayed = 5
        st.session_state.papers = []
        with st.spinner('Wait for it...'):
            st.session_state.papers, papers_amount = st.session_state.sd.scrape_query_results(query, override_max_offset=offset - 100)
        st.success(f'{papers_amount} papers collected!')
        
    if len(st.session_state.papers):
        display_papers()
        def increase_papers():    
            st.session_state["num_displayed"] += 5
        col1, col2 = st.columns(2)
        with col1:
            st.button("Show more", on_click=increase_papers, use_container_width=True)
        with col2:
            scrape_btn = st.button("Chat", type="primary", use_container_width=True)
        if scrape_btn:
            with st.spinner('Loading articles...'):
                st.session_state.sd.scrape_articles()
            st.session_state.active_page = "ChatBot"   
            st.experimental_rerun()

    
