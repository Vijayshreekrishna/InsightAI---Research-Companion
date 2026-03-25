# Insight-AI – Research Companion

**Insight-AI** is a powerful research assistant designed to help students, researchers, and professionals analyze academic papers efficiently. By leveraging advanced Large Language Models (LLMs), it provides simplified summaries, deep comparisons, and actionable future research directions.

## 📖 Features

### Core Modules
- **🧱 Smart Summary**: Generate comprehensive summaries with TL;DR, methodology, and key results. Includes built-in **Voice Summary** for quick listening.
- **💬 Chat with Paper**: Ask questions and get answers grounded strictly in the paper’s text with citations and **RAG History** integration.
- **🆚 Compare Papers**: Upload two papers to see side-by-side differences, similarities, and relative strengths.
- **🔍 Insights & Future Work**: Extract core algorithms, datasets, and keywords, and generate AI-driven suggestions for future research.

### Advanced Modules
- **🔬 Visual Q&A**: Select specific PDF pages to analyze tables, figures, and data using visionary extraction (pdfplumber + Groq).
- **🎙️ Research Pod**: Transform papers into engaging two-person academic podcasts with AI-generated dialogue and audio (gTTS).
- **📚 Local Insights**: Build a persistent semantic library (ChromaDB) to search and query across all your uploaded research papers.
- **🕸️ Citation Graph**: Explore interactive citation networks and paper influence powered by OpenAlex and Pyvis.

## 📁 Project Structure

```
Insight-AI/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── assets/                     # UI assets (CSS, images)
│   └── styles.css
├── pages/                      # Application pages
│   ├── _Chat_with_Paper.py
│   ├── _Citation_Graph.py
│   ├── _Compare_Two_Papers.py
│   ├── _Insights_&_Future_Work.py
│   ├── _Local_Insights.py
│   ├── _Research_Pod.py
│   ├── _Smart_Summary.py
│   └── _Visual_QA.py
├── utils/                      # Core logic and utilities
│   ├── api.py                  # Main API dispatcher and prompt logic
│   ├── citation_utils.py       # OpenAlex and Pyvis network logic
│   ├── gemini_api.py           # Gemini wrapper
│   ├── llm_factory.py          # Multi-provider LLM factory (Gemini, Groq, HF, OpenAI)
│   ├── pdf_utils.py            # PDF text extraction
│   ├── rag_utils.py            # ChromaDB and Semantic Search
│   ├── ui_components.py        # Shared UI elements
│   └── vision_utils.py         # Page rendering and table extraction
└── .env                        # Configuration (API keys)
```

## ⚙️ Setup

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/Vijayshreekrishna/InsightAI---Research-Companion.git
   cd InsightAI---Research-Companion
   ```

2. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure Environment:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   GEMINI_API_KEY=your_key_here
   GROQ_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   HF_TOKEN=your_token_here
   ```

## 🚀 Usage

Run the local server:
```powershell
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.
