import os
import uuid
from flask import Flask, request, jsonify, render_template, session
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


@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Ambil session_id atau buat yang baru
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['session_id'] = session_id  # Simpan session_id ke dalam session Flask

        # Ambil atau buat memori untuk session ini
        memory = get_or_create_memory(session_id)
        
        # Load template prompt dari file
        prompt_template = load_prompt_from_file()
        
        if not prompt_template:
            return jsonify({"error": "Prompt template could not be loaded"}), 400

        # Ambil data dari request JSON
        data = request.json or {}

        # Siapkan input data untuk prompt
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

        # Buat LangChain dengan memori dan prompt
        chain = create_chain(prompt_template, memory)

        # Jalankan chain dan dapatkan hasilnya
        result = chain.invoke(inputs)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
