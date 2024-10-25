import streamlit as st
from query import run_chatbot

prompt = st.chat_input("Say something")
online_toggle= st.toggle(label='enable online lookup',value=False)

if prompt:
    st.write(f"User: {prompt}")
    st.write(run_chatbot(prompt,ext_search= online_toggle))


