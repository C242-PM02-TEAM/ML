import os
import uuid
from flask import Flask, request, json, jsonify, render_template, session
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

        # Prepare inputs
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

        # Generate result
        chain = create_chain(prompt_template, memory)
        result = chain.invoke(inputs)

        # Log raw output
        print("Raw result text:", result["text"])

        # Parse and clean result
        cleaned_result = json.loads(result["text"])

        # Merge paragraphs if necessary
        if "Problem Statement" in cleaned_result:
            problem_statement = cleaned_result["Problem Statement"]
            if isinstance(problem_statement, dict):  # Merge paragraphs
                cleaned_result["Problem Statement"] = " ".join(
                    value for key, value in problem_statement.items() if value
                )

        if "Objective" in cleaned_result:
            objective = cleaned_result["Objective"]
            if isinstance(objective, dict):  # Merge paragraphs
                cleaned_result["Objective"] = " ".join(
                    value for key, value in objective.items() if value
                )

        final_result = {key: value for key, value in cleaned_result.items() if key not in ["human_input", "text"]}

        return jsonify(final_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)
