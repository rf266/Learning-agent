import streamlit as st
import requests

st.header("AI CODING AGENT")

st.text_area("type in code/concepts", height=300)

st.text_area("response", height=100)

st.button("Submit")