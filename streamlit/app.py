import streamlit as st
import requests

st.title("RAG System")

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
if uploaded_file is not None:
    files = {"file": uploaded_file}
    response = requests.post("http://fastapi:8000/upload", files=files)
    if response.ok:
        st.success("PDF uploaded successfully!")
    else:
        st.error("Error uploading PDF: " + response.json().get("error", "Unknown error"))


# Ask a question
question = st.text_area("Ask a question about the uploaded document or URL")
if st.button("Submit Question"):
    if question:
        response = requests.post("http://fastapi:8000/query", json={"question": question})
        if response.ok:
            data = response.json()
            st.markdown(f"**Q:** {data['question']}")
            st.markdown(f"**A:** {data['retrieved_chunks']}")
        else:
            st.error("Error querying: " + response.json().get("error", "Unknown error"))
    else:
        st.error("Please enter a question.")

# Optional: Display processing status
if st.session_state.get("processing"):
    st.spinner("Processing...")

# Optional: Add a history of questions/answers in a sidebar
if "history" not in st.session_state:
    st.session_state.history = []

if st.button("Show History"):
    st.sidebar.header("History")
    for entry in st.session_state.history:
        st.sidebar.write(entry)

if st.button("Submit Question"):
    if question:
        response = requests.post("http://fastapi:8000/query", json={"question": question})
        if response.ok:
            data = response.json()
            st.markdown(f"**Q:** {data['question']}")
            st.markdown(f"**A:** {data['retrieved_chunks']}")
            # Store in history
            st.session_state.history.append({"question": data['question'], "answer": data['retrieved_chunks']})
        else:
            st.error("Error querying: " + response.json().get("error", "Unknown error"))
    else:
        st.error("Please enter a question.")
