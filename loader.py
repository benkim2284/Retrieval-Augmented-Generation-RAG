import json
import os
import shutil
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain_openai import ChatOpenAI
from nltk.tokenize import sent_tokenize

api_key = <API_KEY>
DATA_PATH = "data/investment_banking"
CHROMA_PATH = "chroma"


def load_documents():
    loader = DirectoryLoader(DATA_PATH, "*.md")
    documents = loader.load()
    return documents


def _split_text_sentences_helper(document, sentence_size, overlap_size):
    content = document.page_content
    sentences = sent_tokenize(content)
    chunks = []
    for i in range(0, len(sentences), sentence_size - overlap_size):
        chunk_sentences = sentences[i:i+sentence_size]
        meta_data_with_sentence_index = document.metadata.copy()
        meta_data_with_sentence_index["sentence_start_index"] = i
        if chunk_sentences:
            chunk_content = ' '.join(chunk_sentences)
            chunk_document = Document(page_content=chunk_content, metadata=meta_data_with_sentence_index)
            chunks.append(chunk_document)
    return chunks

def split_text_sentences(documents: list[Document]):
    all_chunks = []
    for doc in documents:
        #depending on whether teacher wants a general quiz or a quiz about a specific worksheet, we will change this.
        chunks = _split_text_sentences_helper(doc, 20, 10)
        all_chunks.extend(chunks)
    return all_chunks

def rewrite_query(user_input):
    model = ChatOpenAI(openai_api_key = api_key, temperature = 0, model="gpt-3.5-turbo")
    rewrite_prompt = f"""
    Respond with only a JSON with the key "search_query", where the value is the academic topic specified
    in the following question. The question is: {user_input}.
    """
    rewritten_query = json.loads(model.invoke(rewrite_prompt).content)["search_query"]
    print(rewritten_query)
    return rewritten_query


def save_to_chroma(chunks: list[Document]):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(chunks, OpenAIEmbeddings(openai_api_key = api_key), persist_directory=CHROMA_PATH)
    db.persist()

def embed_user(user_input):
    embedding_function = OpenAIEmbeddings(openai_api_key = api_key)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    results = db.similarity_search_with_relevance_scores(user_input, k=5)
    print([a[1] for a in results])
    return results


def main():
    #loading documents, and then saving it into vector database
    documents = load_documents()
    chunks = split_text_sentences(documents)
    save_to_chroma(chunks)

    #user prompt and vector database query
    print("\n\n\n\n\n\n\n")
    user_input = input("User:\n")
    print()
    print()
    rewritten_query = rewrite_query(user_input)
    relevant_context = embed_user(rewritten_query)
    relevant_context_text = "\n\n---\n\n".join(doc.page_content for doc, _ in relevant_context)


    #prompt format
    prompt_template = f"""
    Answer the question based only on the following context:

    <context>
    {relevant_context_text}
    </context>

    Answer the following question based on the context provided above: {user_input}
    """

    #model
    model = ChatOpenAI(openai_api_key = api_key, temperature = 0, model="gpt-3.5-turbo")
    print("Itaewon LLM:")
    print(model.invoke(prompt_template).content)
    print()
    sources = [(doc.metadata["source"], doc.metadata["sentence_start_index"]) for doc, _ in relevant_context]
    print(sources)

main()
