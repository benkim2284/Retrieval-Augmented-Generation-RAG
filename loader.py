import os
import shutil
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain_openai import ChatOpenAI

api_key = <API KEY>
DATA_PATH = "data/itaewon_class"
CHROMA_PATH = "chroma"

def load_documents():
    loader = DirectoryLoader(DATA_PATH, "*.md")
    documents = loader.load()
    return documents

def split_text(documents:list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 250,
        length_function = len,
        add_start_index = True
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def save_to_chroma(chunks: list[Document]):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(chunks, OpenAIEmbeddings(openai_api_key = api_key), persist_directory=CHROMA_PATH)
    db.persist()

def embed_user(user_input):
    embedding_function = OpenAIEmbeddings(openai_api_key = api_key)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    results = db.similarity_search_with_relevance_scores(user_input, k=4)
    return results




def main():
    #loading documents, and then saving it into vector database
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)

    #user prompt and vector database query
    print("\n\n\n\n\n\n\n")
    user_input = input("User:\n")
    print()
    print()
    relevant_context = embed_user(user_input)
    relevant_context_text = "\n\n---\n\n".join(doc.page_content for doc, _ in relevant_context)


    #prompt format
    prompt_template = f"""
    Answer the question based only on the following context:

    {relevant_context_text}

    ---

    Answer the following question based on the context provided above: {user_input}
    """

    #model
    model = ChatOpenAI(openai_api_key = api_key)
    print("Itaewon LLM:")
    print(model.invoke(prompt_template).content)
    print()
    sources = [(doc.metadata["source"], f"char_start_index: {doc.metadata['start_index']}") for doc, _ in relevant_context]
    print(sources)






main()
# print(a[0][0].metadata)
