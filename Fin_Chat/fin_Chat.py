import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# === SETUP ===
# Ensure GOOGLE_API_KEY is set in environment variables
# os.environ["GOOGLE_API_KEY"] = "your-api-key-here"  # Uncomment and replace with your actual key
CHROMA_PATH = "chroma"  # Directory where Chroma vector database is stored

# === STEP 1: Load Existing Chroma Vector Store ===
def load_vectorstore():
    """Load existing Chroma vector store."""
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
        # Check if the vector store has documents
        if vectorstore._collection.count() == 0:
            print(f"Error: Chroma database at {CHROMA_PATH} is empty.")
            return None
        return vectorstore
    except Exception as e:
        print(f"Error loading vector store from {CHROMA_PATH}: {e}")
        return None

# === STEP 2: Query Using Retrieval ===
def run_query(vectorstore, query):
    """Run a query using RetrievalQA chain with a custom prompt."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # Retrieve top 3 chunks
    PROMPT_TEMPLATE = """
    Answer the question based only on the following context:
    {context}
    Answer the question based on the above context: {question}
    If the context does not contain relevant information for the requested time period, state that no data is available.
    """
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    
    qa = RetrievalQA.from_chain_type(
        llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, google_api_key=os.environ["GOOGLE_API_KEY"]),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template}
    )
    result = qa.invoke({"query": query})
    
    # Check if relevant results were found
    if not result["source_documents"]:
        return "Unable to fetch a matching result: No relevant documents found."
    max_score = max([doc.metadata.get("relevance_score", 0) for doc in result["source_documents"]])
    if max_score < 0.3:  # Lowered threshold
        return f"Unable to fetch a matching result: Highest relevance score ({max_score:.2f}) is below threshold."
    return result["result"]

# === MAIN ===
if __name__ == "__main__":
    print("\n[1] Loading vector store...")
    vectorstore = load_vectorstore()
    if not vectorstore:
        print("Error: Failed to load vector store. Ensure the Chroma database exists at", CHROMA_PATH)
        exit(1)
    
    print("[2] Ready! You can now ask questions about financial decisions.\n")

    while True:
        user_query = input("Ask a question about financial decisions (or type 'exit'): ").strip()
        if user_query.lower() in ["exit", "quit"]:
            break
        answer = run_query(vectorstore, user_query)
        print(f"\nAnswer: {answer}\n")