import os
import git
import shutil
import subprocess
import argparse
from urllib.parse import urlparse
from groq import Groq

# --- .env and API Configuration ---
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
try:
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('"\'')
except FileNotFoundError:
    raise ValueError(f"CRITICAL ERROR: .env file not found at path: {env_path}")

if "GROQ_API_KEY" in os.environ:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
else:
    raise ValueError("Error: GROQ_API_KEY could not be loaded from the .env file.")


def clone_repo(repo_url):
    """
    Clones a public GitHub repository to a local directory.
    """
    try:
        repo_name = urlparse(repo_url).path.split('/')[-1].replace('.git', '')
        local_path = os.path.join(os.getcwd(), repo_name)
        if os.path.exists(local_path):
            print(f"Removing existing directory: {local_path}")
            subprocess.run(f'rd /s /q "{local_path}"', shell=True, check=True)
        print(f"Cloning repository: {repo_url}...")
        git.Repo.clone_from(repo_url, local_path)
        print(f"Repository cloned successfully to: {local_path}")
        return local_path
    except Exception as e:
        print(f"Error during setup: {e}")
        return None

def quality_analyst_agent(file_path):
    """
    Analyzes a single code file for code smells and quality issues using Groq.
    """
    print(f"\nRunning Quality Analyst on: {os.path.basename(file_path)}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                code_content = f.read()
            except UnicodeDecodeError:
                print("-> Skipping a file that is not plain text.")
                return None, None
        
        prompt = f"""
        You are an expert code quality analyst. Your task is to identify "code smells" in the following Python code.
        Focus on things like: Long Functions, Large Classes, Duplicate Code, or Overly complex logic.
        Please analyze the code below and provide a concise report. If no issues are found, state "No major code quality issues found."

        IMPORTANT: Your response should contain ONLY the analysis report. Do not include any conversational introductions or summaries about your own expertise.

        --- CODE ---
        {code_content}
        --- END CODE ---
        """
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192",
        )
        response_text = chat_completion.choices[0].message.content
        print("--- Quality Analysis Report ---")
        print(response_text)
        print("------------------------------")
        return response_text, code_content
    except Exception as e:
        print(f"Error analyzing file {file_path}: {e}")
        return None, None

def security_specialist_agent(file_path, code_content):
    """
    Analyzes a single code file for security vulnerabilities using Groq.
    """
    print(f"\nRunning Security Specialist on: {os.path.basename(file_path)}...")
    try:
        prompt = f"""
        You are an expert cybersecurity analyst. Your task is to perform a security audit on the following Python code.
        Focus on common vulnerabilities like Injection flaws, Sensitive Data Exposure (e.g., hardcoded API keys), or Security Misconfiguration.
        For each vulnerability found, describe the risk and suggest a secure coding practice to fix it. If no vulnerabilities are found, state that the code appears secure.

        IMPORTANT: Your response should contain ONLY the analysis report. Do not include any conversational introductions about your skills or ask what I want to talk about.

        --- CODE ---
        {code_content}
        --- END CODE ---
        """
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192",
        )
        response_text = chat_completion.choices[0].message.content
        print("--- Security Analysis Report ---")
        print(response_text)
        print("-------------------------------")
        return response_text
    except Exception as e:
        print(f"Error analyzing file {file_path} for security: {e}")
        return None

def chief_refactorer_agent(original_code, quality_report, security_report):
    """
    Takes analysis reports and refactors the code to address the issues.
    """
    print(f"\nRunning Chief Refactorer...")
    try:
        prompt = f"""
        You are a world-class Senior Staff Software Engineer. Your task is to refactor the given Python code based on the reports from your junior analysts.

        Here is the original code:
        --- ORIGINAL CODE ---
        {original_code}
        --- END ORIGINAL CODE ---

        Here is the report from the Code Quality Analyst:
        --- QUALITY REPORT ---
        {quality_report}
        --- END QUALITY REPORT ---

        Here is the report from the Security Analyst:
        --- SECURITY REPORT ---
        {security_report}
        --- END SECURITY REPORT ---

        Your instructions are:
        1.  Carefully review the reports and the original code.
        2.  Rewrite the entire code file, applying the necessary improvements to address the identified issues.
        3.  Maintain the original functionality of the code. Do not add or remove features.
        4.  Provide a brief, clear summary of the changes you made and why, formatted as comments at the top of the new code.
        5.  Your final output should be ONLY the full, refactored Python code with the summary comments at the top. Do not add any other text or explanations before or after the code block.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
        )
        
        refactored_code = chat_completion.choices[0].message.content
        return refactored_code
    except Exception as e:
        print(f"Error during refactoring: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="An AI-powered assistant that analyzes and refactors code from a GitHub repository."
    )
    parser.add_argument("repo_url", help="The URL of the public GitHub repository to analyze.")
    args = parser.parse_args()

    cloned_path = clone_repo(args.repo_url)
    
    if cloned_path:
        output_dir = os.path.join(os.getcwd(), "refactored_code")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        total_py_files = 0
        for root, _, files in os.walk(cloned_path):
            for file in files:
                if file.endswith('.py'):
                    total_py_files += 1
        
        print(f"\nFound {total_py_files} Python files in the repository.")

        LARGE_REPO_THRESHOLD = 20
        analysis_limit = 1
        print(f"Info: To demonstrate the full pipeline, the analysis limit is set to {analysis_limit}.")
        
        print(f"\n--- Starting Full Multi-Agent Pipeline (limit: {analysis_limit} file) ---")
        
        files_analyzed_count = 0
        for root, _, files in os.walk(cloned_path):
            if files_analyzed_count >= analysis_limit:
                break
            for file in files:
                if files_analyzed_count >= analysis_limit:
                    break
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    quality_report, original_code = quality_analyst_agent(file_path)
                    
                    if original_code and quality_report:
                        security_report = security_specialist_agent(file_path, original_code)
                        
                        if security_report:
                            refactored_code = chief_refactorer_agent(original_code, quality_report, security_report)
                            
                            if refactored_code:
                                output_file_path = os.path.join(output_dir, f"refactored_{os.path.basename(file_path)}")
                                with open(output_file_path, 'w', encoding='utf-8') as f:
                                    f.write(refactored_code)
                                print(f"\nRefactored code saved to: {output_file_path}")
                    
                    files_analyzed_count += 1
            
        print("\n--- All Agents Finished ---")
        print(f"Cleaning up directory: {cloned_path}")
        subprocess.run(f'rd /s /q "{cloned_path}"', shell=True)