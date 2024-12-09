import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOpenAI
from langchain.callbacks import StreamingStdOutCallbackHandler
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager
from typing import Dict

# Load environment variables
load_dotenv()

# Dictionary untuk menyimpan memory untuk setiap session
conversation_memories: Dict[str, ConversationBufferMemory] = {}

# Initialize Langsmith client and tracer
client = Client()
tracer = LangChainTracer(project_name=os.getenv("LANGCHAIN_PROJECT"))

# Setup callback manager
callback_manager = CallbackManager([StreamingStdOutCallbackHandler(), tracer])

# Initialize OpenAI LLM with LangChain
llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4",  # Bisa disesuaikan, seperti "gpt-3.5-turbo" jika diinginkan
    temperature=0.7,
    streaming=True,
    callback_manager=callback_manager
)

def get_or_create_memory(session_id: str) -> ConversationBufferMemory:
    """Get or create memory for a session."""
    if session_id not in conversation_memories:
        # Tidak menyimpan chat_history, hanya menyimpan human input
        conversation_memories[session_id] = ConversationBufferMemory(
            memory_key="human_input",
            input_key="human_input"  # Memasukkan human input
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

            # Tambahkan instruksi eksplisit untuk struktur output
            personas = """
            Please generate a structured JSON response based on the following input data.
            For each section (e.g., Problem Statement, Objective), provide the content in a single string without splitting into "Paragraph 1", "Paragraph 2", or similar.
            Ensure the response includes:
            - Metadata
            - Overview
            - Input Overview
            - Problem Statement
            - Objective
            - DARCI Table
            - Project Timeline
            - Success Metrics
            - User Stories
            Make sure the response is valid JSON with double quotes for keys and values.
            """

            prompt_text = personas + "\n\n" + prompt_text

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


