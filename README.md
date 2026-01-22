# Insight-AI – Research Companion

**Insight-AI** is a powerful research assistant designed to help students, researchers, and professionals analyze academic papers efficiently. By leveraging advanced Large Language Models (LLMs), it provides simplified summaries, deep comparisons, and actionable future research directions.

## Features

- **🧱 Smart Summary**: Generate comprehensive summaries with TL;DR, methodology, and key results.
- **💬 Chat with Paper**: Ask questions and get answers grounded strictly in the paper's text with citations.
- **🆚 Compare Papers**: Upload two papers to see side-by-side differences, similarities, and relative strengths.
- **🔍 Insights & Future Work**: Extract core algorithms, datasets, and keywords, and generate AI-driven suggestions for future research.
- **🎧 Voice Summary**: Listen to summaries on the go with built-in text-to-speech.

## Project Structure

```
gdg/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── assets/                     # UI assets (CSS, images)
│   └── styles.css
├── pages/                      # Application pages
│   ├── _Chat_with_Paper.py
│   ├── _Compare_Two_Papers.py
│   ├── _Insights_&_Future_Work.py
│   └── _Smart_Summary.py
├── utils/                      # Core logic and utilities
│   ├── api.py                  # Main API dispatcher and prompt logic
│   ├── gemini_api.py           # Legacy Gemini wrapper (deprecated/referenced)
│   ├── llm_factory.py          # Multi-provider LLM factory (Gemini, Groq, HF, OpenAI)
│   ├── pdf_utils.py            # PDF text extraction
│   └── ui_components.py        # Shared UI elements
└── .env                        # Configuration (API keys)
```

## Setup

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
   # Optional:
   GROQ_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ```

## Usage

Run the local server:
```powershell
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.
