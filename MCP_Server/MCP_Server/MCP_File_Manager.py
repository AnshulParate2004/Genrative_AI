from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import json
import os
from bs4 import BeautifulSoup
import subprocess
import asyncio
import os
from typing import Optional, Literal

load_dotenv()

mcp = FastMCP("MCP_File_Manager")

USER_AGENT = "docs-app/1.0"

@mcp.tool()
async def run_command(command: str, shell: bool = True):
    """
    Execute system commands asynchronously (pip, npm, git, etc.).
    
    Args:
        command: Command string to execute
        shell: Run through shell (default: True)
    
    Returns:
        Formatted output with stdout, stderr, and return code
    
    Examples:
        run_command("pip install langchain")
        run_command("python --version")
        run_command("npm install express")
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
    Create new file or overwrite/append to existing file.
    Auto-creates parent directories if missing.
    
    Args:
        filepath: Absolute or relative file path
        content: Text content to write
        mode: "w" to overwrite (default), "a" to append
    
    Returns:
        Success message with file path and size
    
    Examples:
        write_file("./app.py", "print('Hello')")
        write_file("D:/notes.txt", "New line", mode="a")
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
async def append_to_file(filepath: str, content: str, position: str = "end", marker: str = ""):
    """
    Add content at semantic positions using text markers.
    Ideal for code structure-aware insertions.
    
    Args:
        filepath: Path to existing file
        content: Text to insert
        position: "end", "before_marker", "after_marker", "before_last_line"
        marker: Search text (required for marker-based positions)
    
    Returns:
        Success message with insertion details
    
    Examples:
        append_to_file("app.py", "def new():\\n    pass")
        append_to_file("app.py", "import os\\n", "before_marker", "if __name__")
        append_to_file("config.py", "DEBUG=True\\n", "after_marker", "# Settings")
    """
    try:
        abs_path = os.path.abspath(filepath)
        
        # Read existing content
        if not os.path.exists(abs_path):
            return f"Error: File does not exist: {abs_path}"
        
        with open(abs_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Determine where to insert
        if position == "end":
            new_content = existing_content + content
        
        elif position == "before_last_line":
            lines = existing_content.split('\n')
            if len(lines) > 0:
                lines.insert(-1, content.strip())
                new_content = '\n'.join(lines)
            else:
                new_content = content
        
        elif position == "before_marker":
            if not marker:
                return "Error: marker is required for 'before_marker' position"
            
            if marker in existing_content:
                new_content = existing_content.replace(marker, f"{content}\n{marker}", 1)
            else:
                return f"Error: Marker '{marker}' not found in file"
        
        elif position == "after_marker":
            if not marker:
                return "Error: marker is required for 'after_marker' position"
            
            if marker in existing_content:
                parts = existing_content.split(marker, 1)
                new_content = f"{parts[0]}{marker}\n{content}{parts[1]}"
            else:
                return f"Error: Marker '{marker}' not found in file"
        
        else:
            return f"Error: Unknown position '{position}'. Use: end, before_marker, after_marker, before_last_line"
        
        # Write updated content
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        new_size = os.path.getsize(abs_path)
        added_chars = len(content)
        
        result = f"Successfully appended to file!\n"
        result += f"Path: {abs_path}\n"
        result += f"Position: {position}\n"
        if marker:
            result += f"Marker: {marker}\n"
        result += f"New file size: {new_size} bytes\n"
        result += f"Content added: {added_chars} characters"
        
        print(result)
        return result
        
    except Exception as e:
        error_msg = f"Error appending to file: {str(e)}"
        print(error_msg)
        return error_msg

@mcp.tool()
async def read_file(filepath: str):
    """
    Read complete file content with metadata.
    
    Args:
        filepath: Path to file (absolute or relative)
    
    Returns:
        File content with path and size information
    
    Examples:
        read_file("./config.json")
        read_file("D:/projects/app.py")
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
    List files/directories with optional glob pattern filtering.
    
    Args:
        directory: Directory path (default: current)
        pattern: Glob pattern like "*.py", "test_*", "*" (default: all)
    
    Returns:
        Formatted list with file types and sizes
    
    Examples:
        list_files("./src")
        list_files("D:/projects", "*.json")
        list_files(".", "test_*.py")
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
    Launch file in VS Code editor.
    Searches common installation paths automatically.
    
    Args:
        filepath: File path (absolute or relative)
    
    Returns:
        Success confirmation or error message
    
    Examples:
        open_in_vscode("./app.py")
        open_in_vscode("D:/config.json")
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

@mcp.tool()
async def delete_text_from_file(file_path: str, position: int, length: int):
    """
    Remove specific character range from file.
    Precise deletion using character index position.
    
    Args:
        file_path: Path to file
        position: Start index (0-indexed)
        length: Number of characters to delete
    
    Returns:
        Success message with deletion preview
    
    Examples:
        delete_text_from_file("file.txt", position=10, length=5)
        delete_text_from_file("./notes.txt", position=0, length=20)
    """
    try:
        abs_path = os.path.abspath(file_path)
        
        # Check if file exists
        if not os.path.exists(abs_path):
            return f"Error: File does not exist: {abs_path}"
        
        # Read the entire file content
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        
        # Validate position
        if position < 0:
            return f"Error: Position cannot be negative (got {position})"
        
        if position >= original_size:
            return f"Error: Position {position} is out of range (file has {original_size} characters)"
        
        # Validate length
        if length <= 0:
            return f"Error: Length must be positive (got {length})"
        
        # Calculate end position for deletion
        end_position = position + length
        
        if end_position > original_size:
            # Adjust length if it exceeds file size
            actual_length = original_size - position
            end_position = original_size
            warning = f"\nWarning: Requested length {length} exceeds file size. Deleting {actual_length} characters instead."
        else:
            actual_length = length
            warning = ""
        
        # Extract the text that will be deleted (for preview)
        deleted_text = content[position:end_position]
        
        # Create new content by excluding the deleted range
        new_content = content[:position] + content[end_position:]
        
        # Write the modified content back to file
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        new_size = len(new_content)
        
        # Build result message
        result = f"SUCCESS: Text deleted from file!\n"
        result += f"Path: {abs_path}\n"
        result += f"Deletion start: Character index {position}\n"
        result += f"Characters deleted: {actual_length}\n"
        result += f"Deleted text: '{deleted_text}'\n"
        result += f"Original size: {original_size} characters\n"
        result += f"New size: {new_size} characters\n"
        result += f"Size reduction: {original_size - new_size} characters"
        
        if warning:
            result += warning
        
        print(result)
        return result
        
    except Exception as e:
        error_msg = f"Error deleting text from file: {str(e)}"
        print(error_msg)
        return error_msg


class FileEditor:
    """Handle precise file editing operations at specific positions."""
    
    @staticmethod
    def edit_at_position(
        filepath: str,
        text_to_insert: str,
        position_type: Literal["line_column", "byte_index"] = "line_column",
        line: Optional[int] = None,
        column: Optional[int] = None,
        byte_index: Optional[int] = None,
        operation: Literal["insert", "replace"] = "insert"
    ) -> dict:
        """
        Edit file at precise coordinates with validation.
        
        Args:
            filepath: Path to file
            text_to_insert: Text to insert/replace
            position_type: "line_column" or "byte_index"
            line: Line number (1-indexed, for line_column mode)
            column: Column offset (0-indexed, for line_column mode)
            byte_index: Byte position (0-indexed, for byte_index mode)
            operation: "insert" or "replace"
        
        Returns:
            Dictionary with success status and details
        """
        try:
            abs_path = os.path.abspath(filepath)
            
            # Validate file exists
            if not os.path.exists(abs_path):
                return {
                    "success": False,
                    "error": f"File does not exist: {abs_path}"
                }
            
            # Read file content
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_size = len(content)
            
            # Calculate position
            if position_type == "line_column":
                result = FileEditor._calculate_line_column_position(
                    content, line, column, abs_path
                )
                if not result["success"]:
                    return result
                position = result["position"]
                
            elif position_type == "byte_index":
                result = FileEditor._calculate_byte_position(
                    content, byte_index, abs_path
                )
                if not result["success"]:
                    return result
                position = result["position"]
                
            else:
                return {
                    "success": False,
                    "error": f"Invalid position_type: '{position_type}'. Use 'line_column' or 'byte_index'"
                }
            
            # Perform edit operation
            if operation == "insert":
                new_content = content[:position] + text_to_insert + content[position:]
                edit_description = f"Inserted {len(text_to_insert)} characters"
                
            elif operation == "replace":
                replace_length = len(text_to_insert)
                new_content = content[:position] + text_to_insert + content[position + replace_length:]
                edit_description = f"Replaced {replace_length} characters"
                
            else:
                return {
                    "success": False,
                    "error": f"Invalid operation: '{operation}'. Use 'insert' or 'replace'"
                }
            
            # Write modified content
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            new_size = len(new_content)
            size_change = new_size - original_size
            
            return {
                "success": True,
                "filepath": abs_path,
                "position_type": position_type,
                "position": position,
                "line": line,
                "column": column,
                "byte_index": byte_index,
                "operation": operation,
                "edit_description": edit_description,
                "text_inserted": text_to_insert,
                "original_size": original_size,
                "new_size": new_size,
                "size_change": size_change
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error editing file: {str(e)}"
            }
    
    @staticmethod
    def _calculate_line_column_position(
        content: str,
        line: Optional[int],
        column: Optional[int],
        filepath: str
    ) -> dict:
        """Calculate byte position from line and column."""
        if line is None or column is None:
            return {
                "success": False,
                "error": "line and column are required for line_column position_type"
            }
        
        # Convert to 0-indexed
        target_line = line - 1
        target_column = column
        
        # Split into lines
        lines = content.split('\n')
        
        # Validate line number
        if target_line < 0 or target_line >= len(lines):
            return {
                "success": False,
                "error": f"Line {line} is out of range (file has {len(lines)} lines)"
            }
        
        # Validate column number
        if target_column < 0 or target_column > len(lines[target_line]):
            return {
                "success": False,
                "error": f"Column {column} is out of range for line {line} (line has {len(lines[target_line])} characters)"
            }
        
        # Calculate byte position
        position = sum(len(line) + 1 for line in lines[:target_line])  # +1 for newline
        position += target_column
        
        return {
            "success": True,
            "position": position
        }
    
    @staticmethod
    def _calculate_byte_position(
        content: str,
        byte_index: Optional[int],
        filepath: str
    ) -> dict:
        """Validate and return byte position."""
        if byte_index is None:
            return {
                "success": False,
                "error": "byte_index is required for byte_index position_type"
            }
        
        # Validate byte index
        if byte_index < 0 or byte_index > len(content):
            return {
                "success": False,
                "error": f"Byte index {byte_index} is out of range (file has {len(content)} bytes)"
            }
        
        return {
            "success": True,
            "position": byte_index
        }


# MCP Tool: Edit File at Position
@mcp.tool()
async def edit_file_at_position(
    filepath: str,
    text_to_insert: str,
    position_type: str = "line_column",
    line: int = None,
    column: int = None,
    byte_index: int = None,
    operation: str = "insert"
):
    """
    Surgical file editing at precise coordinates.
    Edit files without rewriting entire content.
    
    Args:
        filepath: Path to file
        text_to_insert: Text to insert/replace
        position_type: "line_column" or "byte_index"
        line: Line number (1-indexed, required for line_column)
        column: Column offset (0-indexed, required for line_column)
        byte_index: Byte position (0-indexed, required for byte_index)
        operation: "insert" (default) or "replace"
    
    Returns:
        Success message with edit details or error
    
    Examples:
        edit_file_at_position("file.txt", " world", line=1, column=5)
        edit_file_at_position("data.txt", "new", "byte_index", byte_index=100)
        edit_file_at_position("file.txt", "FIXED", line=10, column=0, operation="replace")
    """
    result = FileEditor.edit_at_position(
        filepath=filepath,
        text_to_insert=text_to_insert,
        position_type=position_type,
        line=line,
        column=column,
        byte_index=byte_index,
        operation=operation
    )
    
    if result["success"]:
        output = f"✅ File edited successfully!\n"
        output += f"Path: {result['filepath']}\n"
        output += f"Position Type: {result['position_type']}\n"
        
        if result['position_type'] == "line_column":
            output += f"Location: Line {result['line']}, Column {result['column']}\n"
        else:
            output += f"Location: Byte index {result['byte_index']}\n"
        
        output += f"Operation: {result['operation']}\n"
        output += f"Edit: {result['edit_description']}\n"
        output += f"Text inserted: '{result['text_inserted']}'\n"
        output += f"Original size: {result['original_size']} bytes\n"
        output += f"New size: {result['new_size']} bytes\n"
        output += f"Size change: {'+' if result['size_change'] >= 0 else ''}{result['size_change']} bytes"
        
        return output
    else:
        return f"❌ Error: {result['error']}"


# MCP Tool: Find and Replace Text
@mcp.tool()
async def find_and_replace(
    filepath: str,
    find_text: str,
    replace_text: str,
    all_occurrences: bool = False
):
    """
    Find and replace text in a file.
    Simple text replacement without position calculations.
    
    Args:
        filepath: Path to file
        find_text: Text to find
        replace_text: Text to replace with
        all_occurrences: Replace all occurrences (default: False, only first)
    
    Returns:
        Success message with replacement count
    
    Examples:
        find_and_replace("app.py", "old_name", "new_name")
        find_and_replace("config.txt", "DEBUG=False", "DEBUG=True", all_occurrences=True)
    """
    try:
        abs_path = os.path.abspath(filepath)
        
        if not os.path.exists(abs_path):
            return f"❌ Error: File does not exist: {abs_path}"
        
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        
        # Check if text exists
        if find_text not in content:
            return f"❌ Error: Text '{find_text}' not found in file"
        
        # Count occurrences
        occurrence_count = content.count(find_text)
        
        # Perform replacement
        if all_occurrences:
            new_content = content.replace(find_text, replace_text)
            replaced_count = occurrence_count
        else:
            new_content = content.replace(find_text, replace_text, 1)
            replaced_count = 1
        
        # Write back
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        new_size = len(new_content)
        size_change = new_size - original_size
        
        output = f"✅ Text replaced successfully!\n"
        output += f"Path: {abs_path}\n"
        output += f"Find: '{find_text}'\n"
        output += f"Replace: '{replace_text}'\n"
        output += f"Total occurrences found: {occurrence_count}\n"
        output += f"Replaced: {replaced_count} occurrence(s)\n"
        output += f"Original size: {original_size} bytes\n"
        output += f"New size: {new_size} bytes\n"
        output += f"Size change: {'+' if size_change >= 0 else ''}{size_change} bytes"
        
        return output
        
    except Exception as e:
        return f"❌ Error: {str(e)}"


# MCP Tool: Insert at Line Start/End
@mcp.tool()
async def insert_at_line(
    filepath: str,
    line_number: int,
    text: str,
    position: str = "start"
):
    """
    Insert text at the start or end of a specific line.
    Convenient for adding comments or modifying specific lines.
    
    Args:
        filepath: Path to file
        line_number: Line number (1-indexed)
        text: Text to insert
        position: "start" or "end" of line
    
    Returns:
        Success message with details
    
    Examples:
        insert_at_line("script.py", 5, "# TODO: ", "start")
        insert_at_line("notes.txt", 10, " - DONE", "end")
    """
    try:
        abs_path = os.path.abspath(filepath)
        
        if not os.path.exists(abs_path):
            return f"❌ Error: File does not exist: {abs_path}"
        
        with open(abs_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Validate line number
        if line_number < 1 or line_number > len(lines):
            return f"❌ Error: Line {line_number} is out of range (file has {len(lines)} lines)"
        
        # Get target line (0-indexed)
        target_idx = line_number - 1
        original_line = lines[target_idx]
        
        # Insert text
        if position == "start":
            lines[target_idx] = text + original_line
        elif position == "end":
            # Remove newline if exists, add text, then add newline back
            lines[target_idx] = original_line.rstrip('\n') + text + '\n'
        else:
            return f"❌ Error: Invalid position '{position}'. Use 'start' or 'end'"
        
        # Write back
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        output = f"✅ Text inserted at line {position}!\n"
        output += f"Path: {abs_path}\n"
        output += f"Line number: {line_number}\n"
        output += f"Position: {position}\n"
        output += f"Text inserted: '{text}'\n"
        output += f"Original line: {original_line.rstrip()}\n"
        output += f"New line: {lines[target_idx].rstrip()}"
        
        return output
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
