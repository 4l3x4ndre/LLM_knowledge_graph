# Convert file to knowledge graph  🖊️ 

Convert a text file to a knowledge graph using LLMs.

## Requirements

- Ollama installed with [Llama3 instruct](https://ollama.com/library/llama3:instruct)
- Ollama running at http://localhost:11434/

## Setup

Clone this repository, create a virtual environment, activate it, and create a required folder:

```bash
git clone https://github.com/4l3x4ndre/LLM_knowledge_graph.git;
cd LLM_knowledge_graph ; python3 -m venv venv; source venv/bin/activate; mkdir saved_relations
```

Install requirements:

```bash
pip install -r requirements.txt
```

Create english and french models:

```bash
ollama create relations_extraction_fr -f extraction_model_french.modelfile;
ollama create relations_extraction -f extraction_model.modelfile;
```

## Usage

1. **Launch the server**:

```bash
streamlit run extraction.py
```


2. **Choose the language of the file.**
3. **Upload the text or md file.**

The information retrieval will then start:

![example top page](examples/example_top_page.png)

4. **The knowledge graph will be displayed.**

![example graph 1](examples/example_1.png)

Another example :

![example graph 2](examples/example_2.png)


## More

- Graphs are displayed using [NetworkX](https://networkx.org/) in a planar layout if possible.
- Using plotly, the graph can be **zoomed in and out** and **saved as a png**.
- When submitting an already processed file, the server will ask to recompute information retrieval or **use existing relations** (saved under the `saved_relations` folder).
- If the source is present in the link information, the source will be mentionned as "(s)" in the link label. The destination as "(o)", for "object".
- Red links are links that should be read one after the other to represent the full statement of the text.
- **LLMs** models are created with [Ollama model files](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)


