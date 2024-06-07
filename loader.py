import json
import os
import shutil
from langchain_community.document_loaders import DirectoryLoader
from langchain.schema import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from nltk.tokenize import sent_tokenize

api_key = "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"
CHROMA_PATH = "chroma"

embedding_function = OpenAIEmbeddings(openai_api_key = api_key)
db = Chroma(embedding_function=embedding_function)

def load_documents(user_grade):
    DATA_PATH = f"data/{user_grade}"
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
        chunks = _split_text_sentences_helper(doc, 15, 3)
        all_chunks.extend(chunks)
    return all_chunks

def rewrite_query(user_input):
    model = ChatOpenAI(openai_api_key = api_key, temperature = 0, model="gpt-3.5-turbo")
    rewrite_prompt = f"""
    Respond with only a JSON with the key "search_query", where the value is the academic topic specified
    in the following question. The question is: {user_input}.
    """
    rewritten_query = json.loads(model.invoke(rewrite_prompt).content)["search_query"]
    return rewritten_query


def save_to_chroma(chunks: list[Document]):
    try:
        currIdList = db.get()["ids"]
        print(f"BEFORE DELETION: There are currently {len(currIdList)} chunks in the vector database")
        if (len(currIdList) > 0):
            db.delete(ids=currIdList)
            print(f"AFTER DELETION: There are currently {len(db.get()['ids'])} chunks in the vector database")
        db.from_documents(chunks, OpenAIEmbeddings(openai_api_key=api_key))
        print(f"AFTER INSERTION: There are currently {len(db.get()['ids'])} chunks in the vector database")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

def embed_user(user_input):
    
    results = db.similarity_search_with_relevance_scores(user_input, k=5)
    #printing similarities score for each queried chunk
    print([a[1] for a in results])
    return results


def generate_worksheet(user_grade, user_instructions):
    #loading documents, and then saving it into vector database
    documents = load_documents(user_grade)
    chunks = split_text_sentences(documents)
    save_to_chroma(chunks)

    # #user prompt and vector database query
    # print("\n\n\n\n\n\n\n")
    # user_input = input("User:\n")
    # print()
    # print()
    rewritten_query = rewrite_query(user_instructions)
    print(f"rewritten query: {rewritten_query}")
    relevant_context = embed_user(rewritten_query)
    relevant_context_text = "\n\n---\n\n".join(doc.page_content for doc, _ in relevant_context)


    #prompt format
    # prompt_template = f"""
    # You are a worksheet generator that ensures that the generated questions follow the school curriculum standards.
    # The school curriculum standards are the following:

    # <school curriculum standards>
    # {relevant_context_text}
    # </school curriculum standards>

    # Carefully analyze the curriculum standards specified above and make sure that the worksheet includes both mathematical and conceptual questions.
    # The user's instruction for generating the worksheet is: "{user_instructions}"
    # """

    prompt_template = f'''
    You are a worksheet generator. Generate a worksheet according to these instructions: "{user_instructions}" 

    Ensure that the content of the worksheet aligns with curriculum standards, which are the following: 

    <school curriculum standards>
        {relevant_context_text}
    </school curriculum standards>

    Please provide a variety of question types, including multiple-choice, short answer, and problem-solving, to engage students effectively. 
    The worksheet should include questions/problems, each accompanied by clear instructions if needed.
    Use simple language and provide step-by-step explanations to help students understand the material easily.
    '''
    print(prompt_template)

    #model
    model = ChatOpenAI(openai_api_key = api_key, temperature = 0, model="gpt-3.5-turbo")
    print("Itaewon LLM:")
    model_response = model.invoke(prompt_template).content
    print(model_response)
    print()
    sources = [(doc.metadata["source"], doc.metadata["sentence_start_index"], doc) for doc, _ in relevant_context]
    print(sources)
    return model_response

def hello():
    return "hello"

# generate_worksheet("investment_banking", "Why did Toni get denied from  the club?")

