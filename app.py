from pathlib import Path

import chromadb
import ollama
import streamlit as st

st.set_page_config(
    page_title="Healthcare FAQ Chatbot",
    page_icon="💬"
)

st.title("Healthcare FAQ Chatbot")
st.caption("Portfolio demo using fictional clinic information.")

# Open the database created in your notebook.
project_folder = Path(__file__).resolve().parent
client = chromadb.PersistentClient(
    path=str(project_folder / "chroma_db")
)
collection = client.get_collection(name="healthcare_faqs")


def ask_chatbot(question):
    results = collection.query(
        query_texts=[question],
        n_results=1
    )

    passage = results["documents"][0][0]
    faq_id = results["ids"][0][0]
    source = results["metadatas"][0][0]["source"]

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": (
                    f"Read this passage:\n{passage}\n\n"
                    f"According to the passage, {question}\n"
                    "Answer briefly using only the passage.\n"
                    "If the passage does not contain the answer, "
                    "say 'The FAQs do not provide that information.'"
                )
            }
        ],
        options={"temperature": 0}
    )

    return {
        "answer": response["message"]["content"],
        "retrieved_id": faq_id,
        "source": source,
        "evidence": passage
    }


question = st.chat_input(
    "Ask about appointments, parking, billing, or records"
)

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching FAQs and writing an answer..."):
                result = ask_chatbot(question)

            st.write(result["answer"])

            with st.expander("View retrieved evidence"):
                st.caption(
                    f"{result['retrieved_id']} — {result['source']}"
                )
                st.write(result["evidence"])

        except Exception as error:
            st.error(
                "Could not generate an answer. "
                "Check that Ollama is running."
            )
            st.caption(str(error))