from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_core.prompts.chat import ChatPromptTemplate

import os

class RAG_Resources:
    chunk_size = 100 # No of tokens allowed in a chunk
    chunk_overlap = 10 # Max no of tokens that can be overlapped in a chunk

    ## Declaring Static Resources
    persist_directory = "ai_chaperone/docs/chroma/"

    template_str = ""
    with open("ai_chaperone/utils/chat/rag_prompt_template.txt") as file:
        template_str = file.read()

    rag_prompt_template = ChatPromptTemplate.from_template(template_str)

    ## Model Initialization
    embedding = HuggingFaceInferenceAPIEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        api_key=os.getenv("HF_TOKEN")
    )