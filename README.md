# Pediatrician AI Assistant

A React frontend that connects to a FastAPI backend powered by LangChain and Ollama LLM. The system uses "What to Expect the First Year" book as context to answer baby-related questions.

## Features

- 🎨 Clean, modern interface with smooth animations
- 💬 Real-time question-answering interface
- 📚 Powered by "What to Expect the First Year" book knowledge
- 🎯 Vector database for efficient information retrieval
- 📱 Responsive design for all devices
- ⚡ Fast API responses with typing effect

## Prerequisites

- Python 3.8+
- Node.js 16+
- Ollama with llama3 model installed

## Installation & Setup

### 1. Install Ollama and llama3 model

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the llama3 model
ollama pull llama3
```

### 2. Install Python dependencies

```bash
# Install all required Python packages
pip install -r requirements.txt
```

### 3. Install React dependencies

```bash
cd pediatrician-frontend
npm install
```

## Running the Application

### Option 1: Quick Start (Recommended)

Use the provided start script to launch both services:

```bash
./start_app.sh
```

This will start both the backend and frontend automatically.

### Option 2: Manual Start

#### Start the Backend API

In the root directory:

```bash
python pediatrician.py
```

The API will be available at `http://localhost:8000`

#### Start the React Frontend

In a new terminal, navigate to the frontend directory:

```bash
cd pediatrician-frontend
npm start
```

The frontend will be available at `http://localhost:3000`

## Usage

1. Open your browser and go to `http://localhost:3000`
2. You'll see the clean pediatrician interface
3. Type your baby-related question in the input box
4. Click "Ask Doctor" to get an expert answer
5. The answer will appear with a typing effect

## API Endpoints

- `POST /ask` - Submit a question and get an answer
  - Body: `{"question": "Your question here"}`
  - Response: `{"answer": "The doctor's response"}`
- `POST /add_context` - Adds context about the babies to the knowledge base
  - Body: `{"mia_context": "Context for Mia", "luna_context": "Context for Luna"}`
  - Response: `{"message": "Context added successfully"}`

## Project Structure

```
projects/
├── pediatrician.py              # FastAPI backend
├── requirements.txt             # Python dependencies
├── start_app.sh                 # Quick start script
├── whattoexpectthefirstyear.txt # Knowledge base
├── vector_db/                   # Vector database storage
└── pediatrician-frontend/       # React frontend
    ├── src/
    │   ├── App.js              # Main React component
    │   └── App.css             # Styling
    └── package.json
```

## Dependencies

### Python Dependencies (requirements.txt)
- **fastapi** - Web framework for API
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **langchain-community** - LangChain community integrations
- **langchain-text-splitters** - Text splitting utilities
- **langchain-ollama** - Ollama integration
- **langchain-chroma** - ChromaDB integration
- **langchain** - Core LangChain framework
- **chromadb** - Vector database
- **ollama** - Python client for Ollama

### Frontend Dependencies
- **React** - UI framework
- **Framer Motion** - Animations
- **Axios** - HTTP client

## Technologies Used

- **Backend**: FastAPI, LangChain, Ollama, ChromaDB
- **Frontend**: React, Framer Motion, Axios
- **Styling**: CSS3 with gradients and animations
- **AI Model**: Llama3 via Ollama

## Troubleshooting

- Make sure Ollama is running and the llama3 model is downloaded
- Ensure both backend (port 8000) and frontend (port 3000) are running
- Check that the `whattoexpectthefirstyear.txt` file is in the root directory
- If you get CORS errors, make sure the backend is running before starting the frontend
- If port 8000 is already in use, kill the existing process: `pkill -f "python pediatrician.py"`

## Customization

- Modify the prompt template in `pediatrician.py` to change the AI's personality
- Adjust the vector database chunk size and overlap for different retrieval behavior
- Customize the interface styling by modifying the CSS in `App.css`
- Change the color scheme by updating the CSS variables

## Quick Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt
cd pediatrician-frontend && npm install

# Start application
./start_app.sh

# Manual start (two terminals)
python pediatrician.py
cd pediatrician-frontend && npm start

# Stop services
pkill -f "python pediatrician.py"
pkill -f "npm start"
``` 