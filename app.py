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
from langchain.memory import ConversationBufferMemory
from typing import Dict
import uuid
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager
from datetime import datetime


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Langsmith client and tracer
client = Client()
tracer = LangChainTracer(project_name=os.getenv("LANGSMITH_PROJECT"))

# Setup callback manager
callback_manager = CallbackManager([StreamingStdOutCallbackHandler(), tracer])

# Dictionary untuk menyimpan memory untuk setiap session
conversation_memories: Dict[str, ConversationBufferMemory] = {}

# Initialize Groq LLM with LangChain
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-8b-8192",
    streaming=True,
    callback_manager=callback_manager
)

def get_or_create_memory(session_id: str) -> ConversationBufferMemory:
    """Get or create memory for a session."""
    if session_id not in conversation_memories:
        conversation_memories[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="human_input"
        )
    return conversation_memories[session_id]

<<<<<<< HEAD
=======

>>>>>>> 417fb8696b001df854fd8cb6831804a0412bf485
def create_chain(prompt_template: PromptTemplate, memory: ConversationBufferMemory) -> LLMChain:
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
<<<<<<< HEAD
        # Get session ID or create new one
        session_id = session.get('session_id', str(uuid.uuid4()))
=======
        # Ambil session ID atau buat yang baru jika belum ada
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # Logging untuk debug
        print(f"Session ID: {session_id}")
>>>>>>> 417fb8696b001df854fd8cb6831804a0412bf485
        
        # Ambil atau buat memory untuk session ini
        memory = get_or_create_memory(session_id)
        
        # Get prompt from file or request
        prompt_template = load_prompt_from_file()
        if not prompt_template:
            return jsonify({"error": "Prompt template could not be loaded"}), 400

        # Get data from request and format as JSON
        data = request.json
<<<<<<< HEAD
        data['human_input'] = ""  # Set human_input to empty string if not present
=======
        human_input = data.get('human_input', "")
>>>>>>> 417fb8696b001df854fd8cb6831804a0412bf485

        # Create chain with memory and prompt
        chain = create_chain(prompt_template, memory)

        # Run the chain with the provided input data
        result = chain.predict(
            human_input=human_input, 
            overview=data.get('overview', ""),
            start_date=data.get('start_date', ""),
            end_date=data.get('end_date', ""),
            document_version=data.get('document_version', ""),
            product_name=data.get('product_name', ""),
            document_owner=data.get('document_owner', ""),
            developer=data.get('developer', ""),
            stakeholder=data.get('stakeholder', ""),
            doc_stage=data.get('doc_stage', ""),
            created_date=data.get('created_date', "")
        )

<<<<<<< HEAD
=======
        # Tambahkan input dan output ke memory.chat_memory.messages
        memory.chat_memory.messages.append(HumanMessage(content=human_input))
        memory.chat_memory.messages.append(AIMessage(content=result))

        # Return the result as output
>>>>>>> 417fb8696b001df854fd8cb6831804a0412bf485
        return jsonify({"output": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/get_history', methods=['GET'])
def get_history():
    """Retrieve the conversation history for the current session."""
    session_id = session.get('session_id')
    print(f"Session ID: {session_id}")  # Debugging
    
    memory = get_or_create_memory(session_id)
    history = memory.chat_memory.messages
    
    print(f"Current chat history: {history}")  # Debugging
    
    # Konversi messages ke format yang bisa di-serialize
    formatted_history = []
    for message in history:
        if isinstance(message, HumanMessage):
            formatted_history.append({
                "type": "human",
                "content": message.content
            })
        elif isinstance(message, AIMessage):
            formatted_history.append({
                "type": "ai",
                "content": message.content
            })
    
    return jsonify({"history": formatted_history})




if __name__ == '__main__':
    app.run(debug=True)