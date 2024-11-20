import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from groq import Groq

# Muat environment variables dari file .env
load_dotenv()

# Debugging: Pastikan environment variable berhasil dimuat
print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

# Inisialisasi API Client Groq
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")  # Ambil API key dari environment variable
)

def load_prompt():
    """Load prompt dari prompts.txt."""
    try:
        with open("prompts.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: File 'prompts.txt' tidak ditemukan.")
        return ""

@app.route('/')
def index():
    """Render halaman utama."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Ambil prompt dari request atau file prompts.txt
    data = request.json
    prompt = data.get("prompt", "") or load_prompt()

    if not prompt:
        return jsonify({"error": "Prompt tidak boleh kosong"}), 400

    try:
        # Log prompt untuk debugging
        print(f"Prompt: {prompt}")

        # Permintaan ke Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",  # Ganti dengan model yang valid jika perlu
        )

        # Ambil hasil dari API
        generated_text = chat_completion.choices[0].message.content
        print(f"Generated Text: {generated_text}")  # Log untuk debugging

        # Membagi output menjadi 8 bagian
        sections = generated_text.split("\n")[:8]
        structured_output = {f"Section {i+1}": section.strip() for i, section in enumerate(sections)}

        return jsonify(structured_output)

    except KeyError as e:
        print(f"KeyError: {str(e)}")
        return jsonify({"error": "Respons API tidak valid", "details": str(e)}), 500
    except Exception as e:
        # Menangani error umum
        print(f"Error di generate(): {str(e)}")
        return jsonify({"error": "Gagal menghasilkan teks", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
