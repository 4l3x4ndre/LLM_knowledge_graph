import streamlit as st
import ollama

st.set_page_config(page_title="Chat with LLM",page_icon="💬")

def stream_response():
    stream = ollama.chat(
            model=st.session_state["model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
    for chunk in stream:
        yield chunk['message']['content']


# Set a default model
if "model" not in st.session_state:
    st.session_state["model"] = "llama3"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question!"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        streamed_response = stream_response()
        response = st.write_stream(streamed_response)
    st.session_state.messages.append({"role": "assistant", "content": response})


