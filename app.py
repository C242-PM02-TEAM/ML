import os
import uuid
from flask import Flask, request, jsonify, session
from dotenv import load_dotenv

from helpers import (
    get_or_create_memory,
    load_prompt_from_file,
    create_chain,
    conversation_memories
)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Fungsi validasi JSON output
def validate_output_format(output):
    required_keys = [
        "Metadata", "Overview", "Input Overview", "Problem Statement", 
        "Objective", "DARCI Table", "Project Timeline", "Success Metrics", "User Stories"
    ]
    missing_keys = [key for key in required_keys if key not in output]
    if missing_keys:
        raise ValueError(f"Output JSON is missing required keys: {missing_keys}")
    return True


@app.route('/generate', methods=['POST'])
def generate():
    try:
        session_id = session.get('session_id', str(uuid.uuid4()))
        memory = get_or_create_memory(session_id)
        prompt_template = load_prompt_from_file()

        if not prompt_template:
            return jsonify({"error": "Prompt template could not be loaded"}), 400

        data = request.json or {}

        # Prepare inputs as a dictionary
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
            "created_date": data.get("created_date", "")
        }

        # Ensure inputs are formatted as expected
        prompt_text = prompt_template.format(**inputs)

        # Generate result
        chain = create_chain(prompt_template, memory)
        result = chain.invoke(inputs)  # Pass dictionary as input

        # Validate output format and parse
        try:
            output_json = json.loads(result)
            validate_output_format(output_json)
            return jsonify(output_json)
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
