import streamlit as st
import pandas as pd

def analytics():

    if "title_count" not in st.session_state:
        st.session_state.title_count = []


    st.header("Chat Metrics")
    
    # st.dataframe(df)
    if len(st.session_state.title_count):
        df = pd.DataFrame(st.session_state.title_count)
        st.write("# Global Names DataFrame")
        st.bar_chart(df, x="title", y="count")
