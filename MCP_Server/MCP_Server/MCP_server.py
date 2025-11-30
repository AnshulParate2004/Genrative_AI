from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import json
import os
from bs4 import BeautifulSoup
import subprocess
import asyncio

load_dotenv()

mcp = FastMCP("weatherData")

USER_AGENT = "docs-app/1.0"
SERPER_URL = "https://google.serper.dev/search"

docs_urls = {
    "langchain": "python.langchain.com/docs",
    "llama-index": "docs.llamaindex.ai/en/stable",
    "openai": "platform.openai.com/docs",
}

@mcp.tool()
async def run_command(command: str, shell: bool = True):
    """
    Execute a system command on the PC.
    
    Args:
        command: The command to execute (e.g. "pip install chromadb", "npm install axios")
        shell: Whether to run the command through the shell (default: True)
    
    Returns:
        Command output including stdout, stderr, and return code
    
    Examples:
        - run_command("pip install langchain")
        - run_command("npm install express")
        - run_command("python --version")
        - run_command("dir") or run_command("ls -la")
        - run_command("pip show google-generativeai")
    """
    try:
        print(f"Executing command: {command}")
        
        # Run the command asynchronously
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=shell
        )
        
        # Wait for the command to complete and get output
        stdout, stderr = await process.communicate()
        
        # Decode output
        stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
        
        # Format the output nicely
        output = f"Command: {command}\n"
        output += f"Return Code: {process.returncode}\n"
        output += f"Success: {process.returncode == 0}\n\n"
        
        if stdout_text:
            output += f"Output:\n{stdout_text}\n"
        
        if stderr_text:
            output += f"Errors/Warnings:\n{stderr_text}\n"
        
        print(f"Command completed with return code: {process.returncode}")
        
        return output
        
    except Exception as e:
        error_msg = f"Error executing command: {str(e)}"
        print(error_msg)
        return error_msg

@mcp.tool()
async def write_file(filepath: str, content: str, mode: str = "w"):
    """
    Write content to a file on your PC.
    
    Args:
        filepath: Full path to the file (e.g. "D:/projects/app.py" or "./script.js")
        content: The content to write to the file
        mode: Write mode - "w" for overwrite (default), "a" for append
    
    Returns:
        Success message with file path
    
    Examples:
        - write_file("D:/projects/test.py", "print('Hello World')")
        - write_file("./config.json", '{"key": "value"}')
        - write_file("C:/Users/YourName/Desktop/notes.txt", "My notes", mode="a")
    """
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        
        # Write the file
        with open(filepath, mode, encoding='utf-8') as f:
            f.write(content)
        
        abs_path = os.path.abspath(filepath)
        file_size = os.path.getsize(filepath)
        
        action = "Appended to" if mode == "a" else "Created/Overwritten"
        result = f"{action} file successfully!\n"
        result += f"Path: {abs_path}\n"
        result += f"Size: {file_size} bytes\n"
        result += f"Content length: {len(content)} characters"
        
        print(result)
        return result
        
    except Exception as e:
        error_msg = f"Error writing file: {str(e)}"
        print(error_msg)
        return error_msg

@mcp.tool()
async def read_file(filepath: str):
    """
    Read content from a file on your PC.
    
    Args:
        filepath: Full path to the file to read
    
    Returns:
        File content as string
    
    Examples:
        - read_file("D:/projects/app.py")
        - read_file("./config.json")
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        abs_path = os.path.abspath(filepath)
        file_size = os.path.getsize(filepath)
        
        result = f"File: {abs_path}\n"
        result += f"Size: {file_size} bytes\n"
        result += f"{'='*50}\n"
        result += content
        
        print(f"Read file: {abs_path} ({file_size} bytes)")
        return result
        
    except Exception as e:
        error_msg = f"Error reading file: {str(e)}"
        print(error_msg)
        return error_msg

@mcp.tool()
async def list_files(directory: str = ".", pattern: str = "*"):
    """
    List files in a directory.
    
    Args:
        directory: Directory path (default: current directory)
        pattern: File pattern to match (e.g. "*.py", "*.js", "*") (default: all files)
    
    Returns:
        List of files in the directory
    
    Examples:
        - list_files("D:/projects")
        - list_files(".", "*.py")
        - list_files("C:/Users/YourName/Desktop", "*.txt")
    """
    try:
        import glob
        
        abs_dir = os.path.abspath(directory)
        search_pattern = os.path.join(abs_dir, pattern)
        
        files = glob.glob(search_pattern)
        
        result = f"Directory: {abs_dir}\n"
        result += f"Pattern: {pattern}\n"
        result += f"Found {len(files)} file(s)\n"
        result += f"{'='*50}\n"
        
        for file in files:
            size = os.path.getsize(file) if os.path.isfile(file) else 0
            file_type = "DIR" if os.path.isdir(file) else "FILE"
            result += f"[{file_type}] {os.path.basename(file)} ({size} bytes)\n"
        
        print(f"Listed {len(files)} files in {abs_dir}")
        return result
        
    except Exception as e:
        error_msg = f"Error listing files: {str(e)}"
        print(error_msg)
        return error_msg

@mcp.tool()
async def open_in_vscode(filepath: str):
    """
    Open a file in VS Code.
    
    Args:
        filepath: Full path to the file to open in VS Code
    
    Returns:
        Success message
    
    Examples:
        - open_in_vscode("D:/projects/app.py")
        - open_in_vscode("./config.json")
    """
    try:
        abs_path = os.path.abspath(filepath)
        
        # Try common VS Code paths on Windows
        vscode_paths = [
            'code',  # If in PATH
            r'C:\Users\KAIZEN\AppData\Local\Programs\Microsoft VS Code\Code.exe',
            r'C:\Program Files\Microsoft VS Code\Code.exe',
            r'C:\Program Files (x86)\Microsoft VS Code\Code.exe',
        ]
        
        for vscode_path in vscode_paths:
            try:
                process = await asyncio.create_subprocess_shell(
                    f'"{vscode_path}" "{abs_path}"',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                await process.communicate()
                
                if process.returncode == 0:
                    result = f"Opened in VS Code: {abs_path}"
                    print(result)
                    return result
            except:
                continue
        
        return "Could not find VS Code installation"
        
    except Exception as e:
        error_msg = f"Error opening in VS Code: {str(e)}"
        print(error_msg)
        return error_msg

# ============== GIT TOOLS ==============

@mcp.tool()
async def git_status(repo_path: str):
    """
    Check the git status of a repository.
    
    Args:
        repo_path: Path to the git repository
    
    Returns:
        Git status output
    
    Examples:
        - git_status("D:/projects/my-app")
        - git_status(".")
    """
    try:
        abs_path = os.path.abspath(repo_path)
        
        process = await asyncio.create_subprocess_shell(
            f'cd /d "{abs_path}" && git status',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        
        stdout, stderr = await process.communicate()
        stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
        
        result = f"Repository: {abs_path}\n"
        result += f"{'='*50}\n"
        
        if process.returncode == 0:
            result += stdout_text
        else:
            result += f"Error: {stderr_text}"
        
        return result
        
    except Exception as e:
        return f"Error checking git status: {str(e)}"

@mcp.tool()
async def git_add(repo_path: str, files: str = "."):
    """
    Stage files for commit in a git repository.
    
    Args:
        repo_path: Path to the git repository
        files: Files to add (default: "." for all files)
    
    Returns:
        Result of git add operation
    
    Examples:
        - git_add("D:/projects/my-app")
        - git_add("D:/projects/my-app", "src/main.py")
        - git_add(".", "*.py")
    """
    try:
        abs_path = os.path.abspath(repo_path)
        
        process = await asyncio.create_subprocess_shell(
            f'cd /d "{abs_path}" && git add {files}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        
        stdout, stderr = await process.communicate()
        stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
        
        if process.returncode == 0:
            result = f"✅ Successfully staged files in {abs_path}\n"
            result += f"Files pattern: {files}\n"
            if stdout_text:
                result += f"\nOutput:\n{stdout_text}"
            if stderr_text:
                result += f"\nWarnings:\n{stderr_text}"
        else:
            result = f"❌ Error staging files: {stderr_text}"
        
        return result
        
    except Exception as e:
        return f"Error executing git add: {str(e)}"

@mcp.tool()
async def git_commit(repo_path: str, message: str):
    """
    Commit staged changes with a message.
    
    Args:
        repo_path: Path to the git repository
        message: Commit message
    
    Returns:
        Result of git commit operation
    
    Examples:
        - git_commit("D:/projects/my-app", "Initial commit")
        - git_commit(".", "Add new feature")
    """
    try:
        abs_path = os.path.abspath(repo_path)
        
        # Escape quotes in commit message
        safe_message = message.replace('"', '\\"')
        
        process = await asyncio.create_subprocess_shell(
            f'cd /d "{abs_path}" && git commit -m "{safe_message}"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        
        stdout, stderr = await process.communicate()
        stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
        
        if process.returncode == 0:
            result = f"✅ Successfully committed changes\n"
            result += f"Repository: {abs_path}\n"
            result += f"Message: {message}\n\n"
            result += stdout_text
        else:
            result = f"❌ Error committing changes:\n{stderr_text}"
        
        return result
        
    except Exception as e:
        return f"Error executing git commit: {str(e)}"

@mcp.tool()
async def git_push(repo_path: str, remote: str = "origin", branch: str = "main"):
    """
    Push commits to remote repository.
    
    Args:
        repo_path: Path to the git repository
        remote: Remote name (default: "origin")
        branch: Branch name (default: "main")
    
    Returns:
        Result of git push operation
    
    Examples:
        - git_push("D:/projects/my-app")
        - git_push(".", "origin", "master")
    """
    try:
        abs_path = os.path.abspath(repo_path)
        
        process = await asyncio.create_subprocess_shell(
            f'cd /d "{abs_path}" && git push {remote} {branch}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        
        stdout, stderr = await process.communicate()
        stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
        
        if process.returncode == 0:
            result = f"✅ Successfully pushed to {remote}/{branch}\n"
            result += f"Repository: {abs_path}\n\n"
            result += stdout_text
            if stderr_text:
                result += f"\n{stderr_text}"
        else:
            result = f"❌ Error pushing to remote:\n{stderr_text}"
        
        return result
        
    except Exception as e:
        return f"Error executing git push: {str(e)}"

@mcp.tool()
async def git_pull(repo_path: str, remote: str = "origin", branch: str = "main"):
    """
    Pull changes from remote repository.
    
    Args:
        repo_path: Path to the git repository
        remote: Remote name (default: "origin")
        branch: Branch name (default: "main")
    
    Returns:
        Result of git pull operation
    
    Examples:
        - git_pull("D:/projects/my-app")
        - git_pull(".", "origin", "master")
    """
    try:
        abs_path = os.path.abspath(repo_path)
        
        process = await asyncio.create_subprocess_shell(
            f'cd /d "{abs_path}" && git pull {remote} {branch}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        
        stdout, stderr = await process.communicate()
        stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
        
        if process.returncode == 0:
            result = f"✅ Successfully pulled from {remote}/{branch}\n"
            result += f"Repository: {abs_path}\n\n"
            result += stdout_text
            if stderr_text:
                result += f"\n{stderr_text}"
        else:
            result = f"❌ Error pulling from remote:\n{stderr_text}"
        
        return result
        
    except Exception as e:
        return f"Error executing git pull: {str(e)}"

@mcp.tool()
async def git_log(repo_path: str, count: int = 10):
    """
    View git commit history.
    
    Args:
        repo_path: Path to the git repository
        count: Number of commits to show (default: 10)
    
    Returns:
        Git log output
    
    Examples:
        - git_log("D:/projects/my-app")
        - git_log(".", 5)
    """
    try:
        abs_path = os.path.abspath(repo_path)
        
        process = await asyncio.create_subprocess_shell(
            f'cd /d "{abs_path}" && git log --oneline -n {count}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        
        stdout, stderr = await process.communicate()
        stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
        
        result = f"Repository: {abs_path}\n"
        result += f"Last {count} commits:\n"
        result += f"{'='*50}\n"
        
        if process.returncode == 0:
            result += stdout_text if stdout_text else "No commits found"
        else:
            result += f"Error: {stderr_text}"
        
        return result
        
    except Exception as e:
        return f"Error viewing git log: {str(e)}"

@mcp.tool()
async def git_branch(repo_path: str, action: str = "list", branch_name: str = ""):
    """
    Manage git branches.
    
    Args:
        repo_path: Path to the git repository
        action: Action to perform - "list", "create", "delete", "switch" (default: "list")
        branch_name: Branch name (required for create/delete/switch)
    
    Returns:
        Result of branch operation
    
    Examples:
        - git_branch("D:/projects/my-app")
        - git_branch(".", "create", "feature-branch")
        - git_branch(".", "switch", "main")
        - git_branch(".", "delete", "old-branch")
    """
    try:
        abs_path = os.path.abspath(repo_path)
        
        if action == "list":
            cmd = f'cd /d "{abs_path}" && git branch -a'
        elif action == "create":
            if not branch_name:
                return "Error: branch_name is required for create action"
            cmd = f'cd /d "{abs_path}" && git branch {branch_name}'
        elif action == "delete":
            if not branch_name:
                return "Error: branch_name is required for delete action"
            cmd = f'cd /d "{abs_path}" && git branch -d {branch_name}'
        elif action == "switch":
            if not branch_name:
                return "Error: branch_name is required for switch action"
            cmd = f'cd /d "{abs_path}" && git checkout {branch_name}'
        else:
            return f"Error: Unknown action '{action}'. Use list/create/delete/switch"
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        
        stdout, stderr = await process.communicate()
        stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
        
        result = f"Repository: {abs_path}\n"
        result += f"Action: {action}\n"
        result += f"{'='*50}\n"
        
        if process.returncode == 0:
            result += stdout_text
            if stderr_text:
                result += f"\n{stderr_text}"
        else:
            result += f"Error: {stderr_text}"
        
        return result
        
    except Exception as e:
        return f"Error managing branches: {str(e)}"

@mcp.tool()
async def git_diff(repo_path: str, file_path: str = ""):
    """
    View changes in the repository.
    
    Args:
        repo_path: Path to the git repository
        file_path: Specific file to check (optional, shows all changes if empty)
    
    Returns:
        Git diff output
    
    Examples:
        - git_diff("D:/projects/my-app")
        - git_diff(".", "src/main.py")
    """
    try:
        abs_path = os.path.abspath(repo_path)
        
        cmd = f'cd /d "{abs_path}" && git diff'
        if file_path:
            cmd += f' "{file_path}"'
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        
        stdout, stderr = await process.communicate()
        stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
        
        result = f"Repository: {abs_path}\n"
        if file_path:
            result += f"File: {file_path}\n"
        result += f"{'='*50}\n"
        
        if process.returncode == 0:
            result += stdout_text if stdout_text else "No changes detected"
        else:
            result += f"Error: {stderr_text}"
        
        return result
        
    except Exception as e:
        return f"Error viewing git diff: {str(e)}"

@mcp.tool()
async def git_init(repo_path: str):
    """
    Initialize a new git repository.
    
    Args:
        repo_path: Path where to initialize the repository
    
    Returns:
        Result of git init operation
    
    Examples:
        - git_init("D:/projects/new-project")
        - git_init(".")
    """
    try:
        abs_path = os.path.abspath(repo_path)
        
        process = await asyncio.create_subprocess_shell(
            f'cd /d "{abs_path}" && git init',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        
        stdout, stderr = await process.communicate()
        stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
        
        if process.returncode == 0:
            result = f"✅ Successfully initialized git repository\n"
            result += f"Path: {abs_path}\n\n"
            result += stdout_text
        else:
            result = f"❌ Error initializing repository:\n{stderr_text}"
        
        return result
        
    except Exception as e:
        return f"Error executing git init: {str(e)}"

@mcp.tool()
async def git_clone(url: str, destination: str = ""):
    """
    Clone a git repository.
    
    Args:
        url: Repository URL to clone
        destination: Destination path (optional)
    
    Returns:
        Result of git clone operation
    
    Examples:
        - git_clone("https://github.com/user/repo.git")
        - git_clone("https://github.com/user/repo.git", "D:/projects/my-repo")
    """
    try:
        cmd = f'git clone "{url}"'
        if destination:
            abs_dest = os.path.abspath(destination)
            cmd += f' "{abs_dest}"'
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        
        stdout, stderr = await process.communicate()
        stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
        
        if process.returncode == 0:
            result = f"✅ Successfully cloned repository\n"
            result += f"URL: {url}\n"
            if destination:
                result += f"Destination: {abs_dest}\n"
            result += f"\n{stdout_text}"
            if stderr_text:
                result += f"\n{stderr_text}"
        else:
            result = f"❌ Error cloning repository:\n{stderr_text}"
        
        return result
        
    except Exception as e:
        return f"Error executing git clone: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
