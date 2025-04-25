from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import TokenTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_chroma import Chroma

from .resource import RAG_Resources
from .message_history import FileChatMessageHistory
from .manager import LLMManager

def setup_rag_agent(filepath: str):
    print("Initializing Vector DB...")
    ## Vector DB Initialization
    vectordb = Chroma(
        collection_name="alz_docs",
        embedding_function=RAG_Resources.embedding,
        persist_directory=RAG_Resources.persist_directory,
    )

    print("Documents available:", vectordb._collection.count())
    ## If Vector DB is empty, reinitialize it.
    if vectordb._collection.count() == 0:
        ## Document Loading
        loader = Docx2txtLoader(filepath)
        data = loader.load()
        text_splitter = TokenTextSplitter(
            chunk_size=RAG_Resources.chunk_size,
            chunk_overlap=RAG_Resources.chunk_overlap
        )
        split_data = text_splitter.split_documents(data)

        ## Vector DB initialization
        vectordb.add_documents(split_data)

    print("Vector DB Initialized Successfully!!")

    ## Chain Initialization
    combine_docs_chain = create_stuff_documents_chain(
        llm=RAG_Resources.llm, 
        prompt=RAG_Resources.rag_prompt_template, 
        output_parser=RAG_Resources.output_parser,
    )

    qa_chain = create_retrieval_chain(
        vectordb.as_retriever(),
        combine_docs_chain
    )

    return qa_chain

def construct_old_chain(manager: LLMManager, sys_prompt: str):
        filemem = FileChatMessageHistory()
        if(filemem.messages == []):
            filemem.add_user_message(sys_prompt)
            filemem.add_ai_message("")
        memory = ConversationBufferMemory(
            chat_memory=filemem
        )
        chat_llm, output_parser = manager.load_default("virtual_assistant")
        convchain = ConversationChain(
            llm = chat_llm,
            memory = memory,
            output_parser = output_parser,
        )
        print("Chain constructed successfully!!")
        return convchain