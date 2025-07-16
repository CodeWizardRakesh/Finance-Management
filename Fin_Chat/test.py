import os
import google.generativeai as genai
import warnings
import json
from flask import Flask, render_template, request, jsonify
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
import requests


def perform_web_search(query, api_key, num_results=3):
    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": num_results
        }
        res = requests.get("https://serpapi.com/search", params=params)
        results = res.json().get("organic_results", [])
        if not results:
            return "No search results found."

        return "\n".join([f"- [{r['title']}]({r['link']})" for r in results])
    except Exception as e:
        return f"Error during web search: {str(e)}"

# Suppress LangChain and Chroma warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")

# Configure Gemini API
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")
genai.configure(api_key=GOOGLE_API_KEY)

# Paths and embedding function
CHROMA_PATH = "chroma"
em_func = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load Chroma database
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=em_func)

# Manager LLM prompt template
MANAGER_PROMPT_TEMPLATE = """
You are a Manager LLM for a Personal Finance Advisor. Your task is to analyze the user query and provided context to determine if a web search is needed and return a JSON object with the following fields:
- "websearch_needed": "yes" if the query requires real-time or external data (e.g., current stock prices, recent financial news), otherwise "no".
- "user_query": the original user query.
- "context": the provided context from the database.

**Input**:
User Query: {query}
Context: {context}

**Instructions**:
- Output only a valid JSON object, no additional text.
- Set "websearch_needed" to "yes" for queries about real-time data, recent events, or information likely missing from the context.
- Include the full user query and context in the JSON.

**Output Format**:
{{
    "websearch_needed": "yes/no",
    "user_query": "{query}",
    "context": "{context}"
}}
"""

# Advisor LLM prompt template
ADVISOR_PROMPT_TEMPLATE = """
You are an Advisor LLM for a Personal Finance Advisor. Your task is to take a JSON object from the Manager LLM and provide a conversational response to the user's query, including a decision suggestion based on financial best practices.

**Input JSON**:
{manager_json}

**Instructions**:
- Use the "user_query" and "context" from the JSON to answer the query.
- If "websearch_needed" is "yes", note that real-time data is unavailable and rely on the context or general financial knowledge.
- Provide a concise, user-friendly response addressing the query.
- Include a **Suggestion** section with actionable financial advice tailored to the query and context.
- If the context is empty or irrelevant, use general financial knowledge.
- Output only the conversational response, no JSON.

**Example**:
- Input: {{"websearch_needed": "yes", "user_query": "What is my money flow pattern in March?", "context": "April data: Income $5,200, Expenses $3,800..."}}
- Output: I don't have March data, but based on your April patterns, your income was $5,200 with expenses of $3,800 (housing, utilities, dining out). You saved $1,000 and invested $400. **Suggestion**: Track March expenses in a budgeting app like YNAB to identify patterns.

- And if any wesearch done pleese display the websearch links to the user as well
"""

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

# Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def process_query():
    data = request.get_json()
    query_text = data.get('query', '')
    search_links_md = ""

    if query_text.lower() in ['exit', 'quit', 'bye']:
        return jsonify({'response': 'Goodbye!'})

    # Retrieve top 3 relevant chunks from Chroma
    result = db.similarity_search(query_text, k=3)

    # Create context from retrieved chunks
    context_text = "\n\n---\n\n".join([doc.page_content for doc in result])

    # Format prompt for Manager LLM
    manager_prompt_template = ChatPromptTemplate.from_template(MANAGER_PROMPT_TEMPLATE)
    manager_prompt = manager_prompt_template.format_messages(context=context_text, query=query_text)

    # Generate JSON response from Manager LLM
    try:
        manager_response = model.generate_content(manager_prompt[0].content)
        # Clean markdown from response
        cleaned_text = manager_response.text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:].strip()
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:].strip()
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3].strip()

        # Parse Manager LLM JSON
        try:
            # Parse Manager LLM JSON
            manager_json = json.loads(cleaned_text)

            # Perform web search if needed
            
            if manager_json.get("websearch_needed") == "yes":
                serpapi_key = os.environ.get("SERPAPI_API_KEY")
                if not serpapi_key:
                    raise ValueError("SERPAPI_API_KEY is not set in environment.")

                search_links_md = perform_web_search(manager_json["user_query"], serpapi_key)
                manager_json["context"] += "\n\n---\n\n**Web Search Results:**\n" + search_links_md

        except json.JSONDecodeError:
            return jsonify({
    'manager_response': manager_json,
    'advisor_response': advisor_response.text,
    'web_links': search_links_md
})

        # Format prompt for Advisor LLM
        advisor_prompt_template = ChatPromptTemplate.from_template(ADVISOR_PROMPT_TEMPLATE)
        advisor_prompt = advisor_prompt_template.format_messages(manager_json=json.dumps(manager_json))

        # Generate response from Advisor LLM
        try:
            advisor_response = model.generate_content(advisor_prompt[0].content)
            return jsonify({
                'manager_response': manager_json,
                'advisor_response': advisor_response.text,
                'web_links': search_links_md  # ✅ include web links here
            })
        except Exception as e:
            return jsonify({
                'manager_response': manager_json,
                'advisor_response': {'error': f"Error generating response with Advisor LLM: {str(e)}"}
            })

    except Exception as e:
        return jsonify({
            'manager_response': {'error': f"Error generating response with Manager LLM: {str(e)}"},
            'advisor_response': None
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)