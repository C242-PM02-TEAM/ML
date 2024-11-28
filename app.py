import os
from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv
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

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Langsmith client and tracer
client = Client()
tracer = LangChainTracer(project_name=os.getenv("LANGSMITH_PROJECT", "my-chat-project"))

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
            return_messages=True
        )
    return conversation_memories[session_id]

def create_chain(template: str, memory: ConversationBufferMemory) -> LLMChain:
    """Create a LangChain chain with memory."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Anda adalah asisten yang membantu dengan percakapan ini. Gunakan riwayat chat untuk memberikan respons yang kontekstual."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    
    return LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True,
        callback_manager=callback_manager
    )

def load_prompt():
    """Load prompt template from prompts.txt."""
    try:
        with open("prompts.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: File 'prompts.txt' tidak ditemukan.")
        return ""

@app.route('/')
def index():
    """Render the main page and initialize session."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get session ID or create new one
        session_id = session.get('session_id', str(uuid.uuid4()))
        
        # Get or create memory for this session
        memory = get_or_create_memory(session_id)
        
        # Get prompt from request or file
        data = request.json
        prompt_text = data.get("prompt", "") or load_prompt()

        if not prompt_text:
            return jsonify({"error": "Prompt tidak boleh kosong"}), 400

        # Create chain with memory and execute
        chain = create_chain(prompt_text, memory)
        result = chain.invoke({"input": prompt_text})
        
        # Log the result for debugging
        print(f"Generated Text: {result['text']}")

        # Split current response into sections
        sections = result['text'].split("\n")[:8]
        structured_output = {
            "current_response": {
                f"Section {i+1}": section.strip() 
                for i, section in enumerate(sections)
            }
        }

        return jsonify(structured_output)

    except Exception as e:
        print(f"Error in generate(): {str(e)}")
        return jsonify({
            "error": "Gagal menghasilkan teks",
            "details": str(e)
        }), 500

@app.route('/clear_memory', methods=['POST'])
def clear_memory():
    """Clear the conversation memory for the current session."""
    try:
        session_id = session.get('session_id')
        if session_id in conversation_memories:
            del conversation_memories[session_id]
        return jsonify({"message": "Memory berhasil dihapus"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_history', methods=['GET'])
def get_history():
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({"error": "No session found"}), 404
            
        # Get runs from Langsmith for this session
        runs = client.list_runs(
            project_name=os.getenv("LANGSMITH_PROJECT", "my-chat-project"),
            filter_=f"tags.session_id = '{session_id}'"
        )
        
        history = []
        for run in runs:
            history.append({
                "timestamp": str(run.start_time),
                "prompt": run.inputs.get("input", ""),
                "response": run.outputs.get("text", "") if run.outputs else "",
                "runtime": str(run.end_time - run.start_time) if run.end_time else None
            })
            
        return jsonify({"history": history})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)