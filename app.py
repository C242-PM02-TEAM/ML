import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory, session
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.memory import ConversationSummaryMemory
from typing import Dict
import uuid
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Verify environment variables
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))
print("LANGCHAIN_API_KEY:", os.getenv("LANGCHAIN_API_KEY"))
print("LANGCHAIN_PROJECT:", os.getenv("LANGCHAIN_PROJECT"))
print("LANGCHAIN_TRACING_V2:", os.getenv("LANGCHAIN_TRACING_V2"))

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Langsmith client and tracer
if os.getenv("LANGCHAIN_TRACING_V2") == "true":
    tracer = LangChainTracer(project_name=os.getenv("LANGCHAIN_PROJECT"))
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler(), tracer])
else:
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Initialize Groq LLM with LangChain
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-8b-8192",
    streaming=True,
    callback_manager=callback_manager
)

# Dictionary for session memory
conversation_memories = {}

def get_or_create_memory(session_id: str) -> ConversationSummaryMemory:
    """Get or create memory for a session."""
    if session_id not in conversation_memories:
        conversation_memories[session_id] = ConversationSummaryMemory(
            llm=llm,
            memory_key="chat_history",
            input_key="human_input"  # Set input_key to 'human_input' as required
        )
    return conversation_memories[session_id]

def create_chain(prompt_template: PromptTemplate, memory: ConversationSummaryMemory) -> LLMChain:
    """Create a LangChain chain with memory."""
    return LLMChain(
        llm=llm,
        prompt=prompt_template,
        memory=memory,
        verbose=True,
        callback_manager=callback_manager
    )

def load_prompt_from_file():
    """Load the prompt template from a file."""
    try:
        with open("prompts.txt", "r") as file:
            prompt_text = file.read().strip()
            return PromptTemplate(
                input_variables=[
                    "human_input", "overview", "start_date", "end_date", "document_version",
                    "product_name", "document_owner", "developer",
                    "stakeholder", "doc_stage", "created_date"
                ],
                template=prompt_text
            )
    except FileNotFoundError:
        print("Error: File 'prompts.txt' not found.")
        return None

@app.route('/')
def index():
    """Render the main page and initialize session."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        print("Request data:", request.json)  # Log incoming data
        
        # Get session ID or create new one
        session_id = session.get('session_id', str(uuid.uuid4()))
        
        # Get or create memory for this session
        memory = get_or_create_memory(session_id)
        
        # Get prompt from file or request
        prompt_template = load_prompt_from_file()
        if not prompt_template:
            return jsonify({"error": "Prompt template could not be loaded"}), 400

        # Get data from request and format as JSON
        data = request.json
        data['human_input'] = data.get('human_input', "")  # Ensure human_input is set
        
        # Handle start_date and end_date logic
        start_date = data.get('start_date', "")
        end_date = data.get('end_date', "")
        
        # Case 1: If both start_date and end_date are not provided, generate a recommended time period
        if not start_date and not end_date:
            # Default to 1-3 months
            start_date = datetime.today().date()
            end_date = start_date + timedelta(days=90)  # Default to 2 months as a recommendation

        # Case 2: If start_date and end_date are provided by the user, use those values
        if start_date and end_date:
            # Ensure the end_date is later than the start_date
            # Convert start_date and end_date from strings to datetime objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if isinstance(start_date, str) else start_date
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if isinstance(end_date, str) else end_date

            if end_date <= start_date:
                return jsonify({"error": "End date must be later than start date."}), 400

        # Convert the dates back to strings in the format needed for the LLM
        start_date_str = start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime) else start_date
        end_date_str = end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime) else end_date

        # Create chain with memory and prompt
        chain = create_chain(prompt_template, memory)

        # Run the chain with the provided input data
        result = chain.predict(
            human_input=data.get('human_input', ""), 
            overview=data.get('overview', ""),
            start_date=start_date_str,
            end_date=end_date_str,
            document_version=data.get('document_version', ""),
            product_name=data.get('product_name', ""),
            document_owner=data.get('document_owner', ""),
            developer=data.get('developer', ""),
            stakeholder=data.get('stakeholder', ""),
            doc_stage=data.get('doc_stage', ""),
            created_date=data.get('created_date', "")
        )

        return jsonify({"output": result}), 200

    except Exception as e:
        print("Error:", e)  # Print the error to the logs for debugging
        return jsonify({"error": str(e)}), 500

@app.route('/clear_memory', methods=['POST'])
def clear_memory():
    """Clear memory for the current session."""
    session_id = session.get('session_id')
    if session_id in conversation_memories:
        del conversation_memories[session_id]
        return jsonify({"message": "Memory cleared successfully"})
    return jsonify({"error": "No memory found for the session"}), 404

@app.route('/get_history', methods=['GET'])
def get_history():
    """Retrieve the conversation history for the current session."""
    session_id = session.get('session_id')
    memory = get_or_create_memory(session_id)
    history = memory.get_history()
    return jsonify({"history": history})

if __name__ == '__main__':
    app.run(debug=True)
