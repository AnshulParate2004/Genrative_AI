import subprocess

python_executable = r"D:\Genrative_AI\venv\Scripts\python.exe"

# Run question generator
subprocess.run([python_executable, "question_variants.py"], check=True)

# Run multi-LLM response generator
subprocess.run([python_executable, "multi_llm_answers.py"], check=True)

# Run aggregator/final answer optimizer
subprocess.run([python_executable, "optimize_final_answer.py"], check=True)
