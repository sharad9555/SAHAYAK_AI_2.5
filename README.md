# Sahayak AI - Free Local AI + AI Vision

Same Sahayak AI app with local text chatbot, Voice Assistant, and a working AI Vision / Visual Assistant. No OpenAI API key required.

## Windows
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
ollama pull llama3.2:1b
ollama pull moondream
uvicorn backend.main:app --reload
```
Open http://127.0.0.1:8000

Keep Ollama running. AI Vision uses the moondream vision model and the chatbot uses llama3.2:1b. If it is already running, do not run `ollama serve` again.

AI Chat uses `llama3.2:1b`; AI Vision uses `moondream`. Vision is assistive information, not medical diagnosis. Product prices are example/prototype values and can change.
