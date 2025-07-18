# AI Code Refactoring Assistant

## Project Overview

This is a command-line tool that uses a multi-agent AI system to analyze and refactor Python code from public GitHub repositories. The goal is to automatically identify and fix issues related to code quality and security.

***

## Core Concept: A Multi-Agent System

Instead of using one large AI prompt, I designed a system with three specialized AI agents that work together as a team:

1.  **The Quality Analyst**: This agent reviews the code to find "code smells" that affect maintainability, such as long functions or inconsistent variable names.
2.  **The Security Analyst**: This agent specifically scans the code for common security vulnerabilities, like hardcoded API keys or other issues from the OWASP Top 10.
3.  **The Refactoring Agent**: This agent acts as a senior developer. It takes the reports from the other two agents and rewrites the original code to address the identified problems.

***

## Technologies Used

-   **Language**: Python 3
-   **AI Model**: Llama 3 (via the Groq API)
-   **Key Libraries**: `argparse`, `GitPython`, `groq`

***

## Setup and Usage

#### 1. Prerequisites
-   Python 3.8+
-   Git

#### 2. Installation
Ⅰ- First, clone the repository and navigate into the project folder:
```bash
git clone <your-repo-url>
cd AI-Code-Assistant
```
Ⅱ- Next, set up and activate a virtual environment:
```bash
# Create the environment
python -m venv venv
# Activate on Windows
venv\Scripts\activate
```
Ⅲ- Then, install the required packages:
```bash
pip install -r requirements.txt
```

#### 3. API Key Configuration
This tool requires a free Groq API key to connect to the Llama 3 model.

1.  Go to the Groq console: [https://console.groq.com/](https://console.groq.com/)
2.  Sign up for a free account.
3.  Navigate to the **API Keys** section and create a new key.
4.  Create a file named `.env` in the main project folder and paste your key into it like this:
```
GROQ_API_KEY="your-key-here"
```

#### 4. Running the Tool
The tool is run from the command line, with the URL of the target GitHub repository passed as an argument.

**Format:**
```bash
python main.py <github_repo_url>
```
**Example:**
```bash
python main.py [https://github.com/pallets/flask](https://github.com/pallets/flask)
```
The refactored code will be saved in a new folder named `refactored_code`.

***

## Challenges Faced

During this project, I ran into a few technical challenges:
-   **API Rate Limiting**: The initial plan to analyze every file in a large repository quickly exhausted the free API quota. I solved this by adding logic to first count the number of files and then apply a smaller, fixed limit for large repositories to ensure the tool could always run a successful demo.
-   **Prompt Engineering**: The AI agents would sometimes give conversational, unhelpful responses. I had to refine the prompts with very specific instructions to ensure they provided direct, actionable reports without the extra "fluff".
-   **Environment Issues**: There were several platform-specific problems, especially on Windows, related to file permissions and ensuring Python packages were installed in the correct virtual environment. This required using more robust methods for file deletion (`subprocess`) and package installation (`python -m pip`).

***

## Possible Future Improvements

-   **Interactive Mode**: Allow the user to review and approve/reject each suggested code change individually.
-   **GitHub Integration**: Automatically create a new branch and open a pull request with the refactored code.
-   **Web Interface**: Build a simple UI using a framework like Streamlit or Gradio to make the tool more accessible.