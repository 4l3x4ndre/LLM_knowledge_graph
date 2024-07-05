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
        The value of 'text' in the document object is the content of 
        the document decomposed per parts (title or ---).
        The LLM will compute relations for each part of the document.
        Working will smaller parts may lead to a loss of context but 
        will give more precised answers while keeping the system prompt
        in sight.

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

        responses = [] # answers of the LLM
        content = ''   # restriction of the answers to relations only

        # If the document include multiple parts, the title of the part
        # will be displayed for its iteration (to keep track of the process)
        nb_parts = len(document['text'])
        track_message = nb_parts > 1
        index = 0

        for text in document['text']:
            index += 1

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
                if track_message:
                    with st.expander(f"*Processing part {index}/{nb_parts}:" + " \"" +  text.split('\n')[0] + "\"*"):
                        st.write(f"```md\n{response['message']['content']}")
                else:
                    with st.expander(f"Retrieval done  🎈"):
                        st.write(f"```md\n{response['message']['content']}")

        
            for line in response['message']['content'].strip().split('\n'):
                relation = line.split('->')
                if len(relation) == 3 and relation[1].strip() != '':
                    content += str(line) + '\n'

            if track_message:
                # If more than one parts, then '---' is used in the file of relations
                # to indicate 'new part' = new graph.
                content += '---\n'
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
        "In which language is the document written?",
        ("Français", "English")
    )
        

    decompose_container = st.container(border=True)
    decompose_file_option = decompose_container.toggle(
            "Do you want the document to be decomposed? (One part per title)",
    )
    if decompose_file_option:
        decompose_container.write("> With this option, the retrieval will **take longer** but \
            will **give more information**. One graph will be generated per level 1 heading of the document \
            (markdown formatting).")

    else:
        decompose_container.write("> The document will be processed as a whole.")

    # Get source file
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is not None: 

        # Read file as string
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        string_data = stringio.read()

        
        documents_parts = ['']
        if decompose_file_option:
            # The document will be decomposed per title

            for line in string_data.split('\n'):
                # Detects new part delimiters (title)
                if line.startswith('# '):
                    documents_parts.append('')

                # Add the current line to the considered part of the document
                # (if the line is relevant)
                if len(line) > 10:
                    documents_parts[-1] += line + '\n'
        else:
            # The document is not decomposed and will be processed as a whole. 
            documents_parts = [string_data]

        # Create document object
        document = {
            "title": uploaded_file.name,
            "text": documents_parts
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
            col1, col2 = st.columns(2)
            if col1.button("yes, recompute", key="yes"):
                button="yes"
                content = compute_relations(document, language_option)

            elif col2.button("no, use existing relations", key="no"):
                button="no"
                with st.chat_message("assistant"):
                    with st.expander("🆗 Processing with existing relations"):
                        st.write("```md\n" + '\n'.join(content) + "```")


        if button:
            with st.chat_message("assistant", avatar='🎨'):
                #create_graphs_from_file('./saved_relations/' + document['title'].split('.')[0] + '.txt')
                create_graphs_from_content(content)
                st.write("Done!  🎈") 


if __name__ == '__main__':
    st.set_page_config(
        page_title="Knowledge Graph",
        page_icon="🖊️"
    )
    extract_relations()
