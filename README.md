# Machine Learning C242-PM02(PRDify)

💡 Our Machine Learning member repository to build and generate for our PRDify Project

## Installation and Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HakimIqbal/LLM-PRD-Maker.git
   cd LLM-PRD-Maker
   ```

2. **Set up environment variables:**
   Create a `.env` file in the root directory and add the following variables:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
   LANGCHAIN_API_KEY="<your-api-key>"
   LANGCHAIN_PROJECT="<your-project-name>"
   ```

3. **Install dependencies:**
   Make sure Python 3.7+ is installed and then run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   Start the Flask development server:
   ```bash
   python app.py
   ```

5. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:5000` to interact with the app.

## API Endpoint

### `POST /generate`

This endpoint receives the PRD data in JSON format and returns a generated PRD in JSON format.

#### Request Body:
```json
{
  "overview": "This document outlines the development of an Academic Information System for Bengkulu University, focusing on user experience and backend integrations.",
  "start_date": "2024-01-01",
  "end_date": "2024-12-01",
  "document_version": "v1.0",
  "product_name": "SIAKAD Blueprint",
  "document_owner": "Bengkulu University IT Department",
  "developer": "John Doe, Jane Smith",
  "stakeholder": "University Leadership, Faculty Members",
  "doc_stage": "Draft",
  "created_date": "2024-12-10"
}
```

#### Example of Testing with Postman:

To test the `/generate` endpoint, you can use a tool like Postman. 

1. Open Postman and create a new **POST** request.
2. Set the request URL to `http://127.0.0.1:5000/generate`.
3. In the **Body** section, select **raw** and set the type to **JSON**.
4. Paste the following input data:

```json
{
  "overview": "This document outlines the development of an Academic Information System for Bengkulu University, focusing on user experience and backend integrations.",
  "start_date": "2024-01-01",
  "end_date": "2024-12-01",
  "document_version": "v1.0",
  "product_name": "SIAKAD Blueprint",
  "document_owner": "Bengkulu University IT Department",
  "developer": "John Doe, Jane Smith",
  "stakeholder": "University Leadership, Faculty Members",
  "doc_stage": "Draft",
  "created_date": "2024-12-10"
}
```

5. Hit the **Send** button to get the generated PRD response.

## Environment Variables

### Required
- **OPENAI_API_KEY**: Your OpenAI API key (if using OpenAI for additional functionality).
- **GROQ_API_KEY**: Your Groq API key for language model access.
- **LANGCHAIN_API_KEY**: Your LangChain API key for using LangChain features.
- **LANGCHAIN_PROJECT**: The project name in LangChain.

### Optional
- **LANGCHAIN_TRACING_V2**: Set to `true` to enable LangChain tracing.
- **LANGCHAIN_ENDPOINT**: The LangChain API endpoint, default is `https://api.smith.langchain.com`.

---

For any issues or feature requests, please open an issue in the GitHub repository.