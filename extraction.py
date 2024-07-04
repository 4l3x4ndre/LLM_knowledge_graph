from io import StringIO
from ollama import Client
from graph import create_graphs_from_content
import streamlit as st
import os # Check if file exists

class OntoGPT:
    def __init__(self):
        self.model =  Client(host='http://localhost:11434')

    def extract_relations(self, document:dict, language:str) -> str:
        """
        Uses the local LLM to extract relations.

        Params:
        document: dict with 'text' and 'title'
        """

        with st.chat_message("brain", avatar="🧠"):
            if language == "Français":
                st.write("Processing in french...")
                model = 'relations_extraction_fr'
            else:
                st.write("Processing in english...")
                model = 'relations_extraction'

        text = document['text']
        response = self.model.chat(
            model=model,
            messages=[
                    {
                    "role": 'user', 
                    "content": f'Give me the relations of this text. Only relation, do not talk to me. \n```md\n{text}\n```'
                }
              ]
        )

        with st.chat_message("brain", avatar="🧠"):
            st.write(f"```md\n{response['message']['content']}```")
        
        content = ''
        for line in response['message']['content'].strip().split('\n'):
            if '->' in line and len(line) > 1:
                content += str(line) + '\n'

        save_file(document['title'].split('.')[0], content)
        return content
   

def save_file(title:str, content:str):
    """
    Params:
    title: without the extension
    content: with \n for lines
    """
    f = open("saved_relations/" + title + ".txt", "w")
    f.write(content)
    f.close()

def file_exists(title:str)->str:
    """
    Returns the file of the content if it exists
    else empty string.
    
    Params:
    title: without the extension
    """
    if os.path.isfile('./saved_relations/' + title + '.txt'):
        f = open('./saved_relations/' + title + '.txt')
        content = f.readlines()
        f.close()
        return content
    return ''

def compute_relations(document:dict, language_option:str) -> str:
    """
    Scan document written in given language and compute relations.

    Returns the relations as text, one relation per line.
    """
    ontogpt = OntoGPT()
    with st.chat_message("assistant"):
        st.write(f"Extracting relations from '*{document['title']}*' ... 🖊️")

    content = ontogpt.extract_relations(document, language_option).split('\n')

    with st.chat_message("assistant"):
        st.write("Extraction finished  🎉 ") 

    return content


def extract_relations():

    st.title("Convert file to graph  🖊️ ")

    language_option = st.selectbox(
        "What language is the document?",
        ("Français", "English")
    )
        
    # Get source file
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is not None: 

        # Read file as string
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        string_data = stringio.read()

        # Create document object
        document = {
            "title": uploaded_file.name,
            "text": string_data
        }

        content = file_exists(document['title'].split('.')[0])
        if not content:
            # The file has never been seen. Compute the relations.

            content = compute_relations(document, language_option)
            button= ' ' # not empty to act as validated

        else:
            # The file has already been processed. Should the relations be recompute?
            button = '' # Empty string to prevent the program to continue

            with st.chat_message("assistant"):
                st.write("Document already scanned. **Re-compute** relations?")

            # Two buttons are proposed to the user. 
            # Yes to recompute, no to use existing relations

            if st.button("yes, recompute", key="yes"):
                button="yes"
                content = compute_relations(document, language_option)

            elif st.button("no, use existing relations", key="no"):
                button="no"
                with st.chat_message("assistant"):
                    st.write("Processing with existing relations:")
                    st.write("```md\n" + '\n'.join(content) + "```")


        if button:
            with st.chat_message("assistant", avatar='🎨'):
                #create_graphs_from_file('./saved_relations/' + document['title'].split('.')[0] + '.txt')
                create_graphs_from_content(content)
                st.write("Done!  🎈") 


if __name__ == '__main__':
    extract_relations()
