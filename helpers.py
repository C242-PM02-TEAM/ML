import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.callbacks import StreamingStdOutCallbackHandler
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager
from typing import Dict

# Dictionary untuk menyimpan memory untuk setiap session
conversation_memories: Dict[str, ConversationBufferMemory] = {}

# Initialize Langsmith client and tracer
client = Client()
tracer = LangChainTracer(project_name=os.getenv("LANGSMITH_PROJECT"))

# Setup callback manager
callback_manager = CallbackManager([StreamingStdOutCallbackHandler(), tracer])

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
            input_key="human_input"  # Set input_key to 'human_input' as required
        )
    return conversation_memories[session_id]

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
