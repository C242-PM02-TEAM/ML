import os
import uuid
from flask import Flask, request, jsonify, session
from dotenv import load_dotenv

from helpers import (
    get_or_create_memory,
    load_prompt_from_file,
    create_chain
)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get session ID or create a new one
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['session_id'] = session_id

        # Get or create memory for this session
        memory = get_or_create_memory(session_id)

        # Load prompt template from file
        prompt_template = load_prompt_from_file()

        if not prompt_template:
            return jsonify({"error": "Prompt template could not be loaded"}), 400

        # Get data from the request (data yang diterima dari frontend)
        data = request.json or {}

        # Prepare the input data as a dictionary
        inputs = {
            "overview": data.get("overview", ""),
            "start_date": data.get("start_date", ""),
            "end_date": data.get("end_date", ""),
            "document_version": data.get("document_version", ""),
            "product_name": data.get("product_name", ""),
            "document_owner": data.get("document_owner", ""),
            "developer": data.get("developer", ""),
            "stakeholder": data.get("stakeholder", ""),
            "doc_stage": data.get("doc_stage", ""),
            "created_date": data.get("created_date", ""),
            "human_input": data.get("human_input", "")
        }

        # Create chain with memory and prompt
        chain = create_chain(prompt_template, memory)

        # Run the chain using invoke
        result = chain.invoke(inputs)

        # Extract text from result if it's a HumanMessage or other non-serializable object
        if isinstance(result, dict):
            response_text = result.get('text', result)
        else:
            response_text = str(result)

        return jsonify({"response": response_text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
