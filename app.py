# app.py

import asyncio
import streamlit as st

from agents.orchestrator import handle_user_query

st.set_page_config(
    page_title="Inkel Tourism Assistant",
    page_icon="🌍",
    layout="centered",
)

st.title("🌍 Multi-Agent Tourism Assistant")
st.write("Ask about weather and tourist places for any city using real data.")

user_input = st.text_input(
    "Type your query:",
    placeholder="Example: I'm going to go to bangalore, what is the temperature there and places to visit?",
)

if st.button("Ask"):
    if not user_input.strip():
        st.warning("Please type a question first.")
    else:
        with st.spinner("Thinking..."):
            # run the async orchestrator
            response_text, debug = asyncio.run(handle_user_query(user_input))

        st.subheader("Response")
        st.write(response_text)

        with st.expander("Debug Info (for assignment / checking)"):
            st.json(debug)
