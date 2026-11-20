# AI Quiz Maker

A small local quiz app built with **PydanticAI**, **Anthropic Claude**, and **Streamlit**. Enter a topic, choose a difficulty and question count, answer the generated multiple-choice questions, and then see your score and explanations.

## Requirements

- Python 3.10 or newer
- An Anthropic API key and access to the model you choose
- Internet access while the app calls Anthropic

Model API requests may incur charges according to your Anthropic account and model pricing.

## Set up and run locally

Open a terminal in this project folder and run:

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks virtual-environment activation, use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

Open `.env` in a text editor and enter your own Anthropic values:

```dotenv
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=anthropic:your-model-id
```

Replace `your-model-id` with the model ID available to your Anthropic account. Keep `.env` private; it is excluded from Git by `.gitignore`.

Start the app:

```powershell
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`) and may open it in your browser. Keep the terminal running while you use the app; press `Ctrl+C` in that terminal to stop it.

## How it works

- PydanticAI asks the configured Anthropic model to return a validated quiz structure.
- Quiz questions and answers are kept in the local Streamlit session while you use the app.
- Answers and explanations are revealed after you submit the quiz.
- Your API key is read from `.env`; never paste it into the source files or commit it.

## Push to GitHub later

When the code is ready, create an empty repository on GitHub (do not initialize it with a README if you plan to push this existing README). Then, from this folder, run:

```bash
git init
git add .
git status --short
git commit -m "Add local PydanticAI quiz maker"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the remote URL with the repository you created. Before committing, check that `.env` is not listed by `git status --short` and never push your API key. Repository creation and pushing are separate steps; this project setup does not publish anything by itself.
