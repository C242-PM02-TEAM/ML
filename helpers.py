import os
import json
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.load.dump import dumps
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager
from typing import Dict

# Load environment variables
load_dotenv()

# Dictionary untuk menyimpan memory untuk setiap session
conversation_memories: Dict[str, ConversationBufferMemory] = {}

# Initialize Langsmith tracer
tracer = LangChainTracer(project_name=os.getenv("LANGCHAIN_PROJECT"))

# Setup callback manager
callback_manager = CallbackManager([StreamingStdOutCallbackHandler(), tracer])

# Initialize ChatOpenAI LLM with LangChain
llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),  # Ganti dengan API Key OpenAI
    model="gpt-4",  # Gunakan model GPT-4 atau model OpenAI lainnya
    temperature=0.7,
    max_tokens=2000,
    streaming=True,
)

def get_or_create_memory(session_id: str):
    """Get or create conversation memory."""
    return ConversationBufferMemory(memory_key="chat_history")

def create_chain(prompt_template: PromptTemplate, memory: ConversationBufferMemory):
    """Create a LangChain LLMChain."""
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

            # Buat PromptTemplate dengan semua input variables
            return PromptTemplate(
                input_variables=[
                    "overview", "start_date", "end_date", "document_version",
                    "product_name", "document_owner", "developer",
                    "stakeholder", "doc_stage", "created_date"
                ],
                template=prompt_text
            )
    except FileNotFoundError:
        print("Error: File 'prompts.txt' not found.")
        return None

def process_result_to_json(result):
    """Process the result to ensure it's JSON serializable."""
    return dumps(result, ensure_ascii=False, indent=2)