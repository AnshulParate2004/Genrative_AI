import os
import json
from typing import Any
from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Scopes for Google Sheets and Forms
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/drive.readonly'
]

# Initialize FastMCP server
mcp = FastMCP("gsheets")

def get_credentials():
    """Get Google API credentials"""
    creds = None

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, 'token.pickle')

    # Token file stores the user's access and refresh tokens
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_sheets_service():
    """Get Google Sheets service"""
    creds = get_credentials()
    return build('sheets', 'v4', credentials=creds)

def get_forms_service():
    """Get Google Forms service"""
    creds = get_credentials()
    return build('forms', 'v1', credentials=creds)

def get_drive_service():
    """Get Google Drive service"""
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)


@mcp.tool()
def list_spreadsheets(max_results: int = 20) -> str:
    """
    List user's Google Spreadsheets

    Args:
        max_results: Maximum number of spreadsheets to return (default: 20)

    Returns:
        JSON string with spreadsheet names, IDs, and URLs
    """
    service = get_drive_service()
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.spreadsheet'",
        pageSize=max_results,
        fields="files(id, name, webViewLink)"
    ).execute()

    files = results.get('files', [])
    spreadsheets = [{
        'name': f['name'],
        'id': f['id'],
        'url': f['webViewLink']
    } for f in files]

    return json.dumps(spreadsheets, indent=2)


@mcp.tool()
def read_sheet(spreadsheet_id: str, range_name: str = "Sheet1") -> str:
    """
    Read data from a Google Sheet

    Args:
        spreadsheet_id: The ID of the spreadsheet (from the URL)
        range_name: The A1 notation of the range to read (default: Sheet1)

    Returns:
        JSON string with the sheet data
    """
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get('values', [])
    return json.dumps(values, indent=2)


@mcp.tool()
def write_sheet(spreadsheet_id: str, range_name: str, values: list) -> str:
    """
    Write data to a Google Sheet

    Args:
        spreadsheet_id: The ID of the spreadsheet
        range_name: The A1 notation of where to write
        values: 2D list of values to write

    Returns:
        Confirmation message
    """
    service = get_sheets_service()
    body = {'values': values}

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

    return f"Updated {result.get('updatedCells')} cells"


@mcp.tool()
def append_sheet(spreadsheet_id: str, range_name: str, values: list) -> str:
    """
    Append data to a Google Sheet

    Args:
        spreadsheet_id: The ID of the spreadsheet
        range_name: The A1 notation of the range
        values: 2D list of values to append

    Returns:
        Confirmation message
    """
    service = get_sheets_service()
    body = {'values': values}

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

    return f"Appended {result.get('updates').get('updatedCells')} cells"


@mcp.tool()
def create_spreadsheet(title: str) -> str:
    """
    Create a new Google Spreadsheet

    Args:
        title: The title of the new spreadsheet

    Returns:
        JSON with spreadsheet ID and URL
    """
    service = get_sheets_service()
    spreadsheet = {
        'properties': {
            'title': title
        }
    }

    result = service.spreadsheets().create(body=spreadsheet).execute()

    return json.dumps({
        'spreadsheet_id': result.get('spreadsheetId'),
        'url': result.get('spreadsheetUrl')
    }, indent=2)


@mcp.tool()
def create_form(title: str, description: str = "") -> str:
    """
    Create a new Google Form

    Args:
        title: The title of the form
        description: Optional description for the form

    Returns:
        JSON with form ID and URL
    """
    service = get_forms_service()
    form = {
        'info': {
            'title': title,
            'documentTitle': title
        }
    }

    if description:
        form['info']['description'] = description

    result = service.forms().create(body=form).execute()

    return json.dumps({
        'form_id': result.get('formId'),
        'url': result.get('responderUri')
    }, indent=2)


# Resources - provide access to sheet data
@mcp.resource("sheet://{spreadsheet_id}/{range_name}")
def get_sheet_resource(spreadsheet_id: str, range_name: str = "Sheet1") -> str:
    """
    Resource for accessing Google Sheet data

    Args:
        spreadsheet_id: The spreadsheet ID
        range_name: The range to read

    Returns:
        Sheet data as text
    """
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get('values', [])

    # Format as readable text
    output = []
    for row in values:
        output.append(' | '.join(str(cell) for cell in row))

    return '\n'.join(output)


# Prompt templates
@mcp.prompt()
def analyze_sheet_data():
    """Analyze data from a Google Sheet with comprehensive insights"""
    return """I need help analyzing data from a Google Sheet. Please follow this workflow:

1. **Data Retrieval & Overview**
   - Ask me for the spreadsheet name and range (or help me list my spreadsheets if needed), unless the user has already retrieved a spreadsheet
   - Read the sheet data using the read_sheet tool
   - Provide a high-level summary:
     * Total number of rows and columns
     * Column headers/names
     * Date range (if applicable)
     * Brief description of what type of data this appears to be

2. **Data Structure Analysis**
   - Identify data types in each column (text, numeric, dates, categorical, etc.)
   - Note which columns contain responses vs. metadata
   - Check for missing, empty, or inconsistent values
   - Identify any obvious patterns in data organization

3. **Quantitative Analysis** (where applicable)
   - Calculate relevant statistics:
     * For numeric columns: averages, ranges (min/max), totals
     * For categorical data: frequency distributions, most common values
     * For rating scales: score distributions and averages
   - Identify any outliers or unusual values

4. **Qualitative Insights** (where applicable)
   - Summarize themes in text responses
   - Identify common keywords or topics
   - Note any particularly interesting or concerning comments
   - Highlight consensus vs. divergent opinions

5. **Key Findings & Recommendations**
   - Summarize 3-5 most important insights from the data
   - Flag any data quality issues or anomalies
   - Suggest improvements (data cleaning, additional fields, validation rules)
   - Recommend next steps for analysis or action
   - Propose visualization options that would make the data clearer

Please present findings in a clear, scannable format with specific examples and numbers from the actual data."""


@mcp.prompt()
def create_report_template():
    """Create a professional report document in the canvas"""
    return """Help me create a professional report document with the following structure. Please create this as a well-formatted markdown document in the canvas:

1. **Report Header**
   - Report title
   - Company name (Lonely Octopus)
   - Report period/date range
   - Date generated

2. **Executive Summary**
   - Brief overview of key findings (2-3 paragraphs)
   - Highlight the most critical insights
   - Bottom-line recommendation or conclusion

3. **Key Metrics Dashboard**
   - Create a clean table with columns: Metric | Value | Change | Status
   - Include 5-8 relevant metrics with placeholder values
   - Add brief context notes below the table

4. **Detailed Analysis**
   - Break down findings into logical sections
   - Use clear headers for each topic area
   - Include supporting data and evidence
   - Present information in scannable format

5. **Findings & Recommendations**
   - **Key Findings**: List 3-5 most important discoveries
   - **Recommendations**: Specific, actionable suggestions
   - **Action Items**: Table with columns for Item, Owner, Due Date, Priority

6. **Appendix/Additional Notes**
   - Methodology or data sources (if applicable)
   - Assumptions made
   - Areas for further investigation
   - Additional context or supporting information

Please format the report with:
- Clear hierarchy using markdown headers
- Professional tables for data presentation
- Bold text for emphasis on key points
- Appropriate spacing for readability
- Placeholder content that can be easily customized"""

@mcp.prompt()
def form_to_sheet():
    """Create a Google Form and spreadsheet workflow for data collection"""
    return """Help me set up a complete data collection workflow using Google Forms and Sheets:

1. **Understand Requirements**
   - Ask me what type of data I want to collect
   - Ask about the purpose (survey, registration, feedback, etc.)
   - Confirm the key fields/questions needed

2. **Create Google Form**
   - Use create_form tool with an appropriate title and description
   - Provide the form URL for editing
   - Suggest question types for each field (short answer, multiple choice, etc.)

3. **Create Response Spreadsheet**
   - Create a new spreadsheet with create_spreadsheet tool
   - Name it to match the form (e.g., "Form Name - Responses")
   - Set up the first row with column headers matching the form questions
   - Add a "Timestamp" column as the first column

4. **Integration Instructions**
   - Provide step-by-step instructions to link the form to the spreadsheet:
     * Open the Form in edit mode
     * Click "Responses" tab
     * Click the green Sheets icon
     * Select "Create a new spreadsheet" or link to existing
   - Note: This step requires manual action in the Google Forms interface

5. **Setup Recommendations**
   - Suggest form settings (collect email, limit to 1 response, etc.)
   - Recommend data validation rules
   - Propose notification settings for new responses
   - Suggest basic formulas or formatting for the response sheet

6. **Provide Summary**
   - Form URL for editing and sharing
   - Spreadsheet URL for viewing responses
   - Quick reference guide for managing the workflow

Please provide all URLs and IDs clearly formatted for easy access."""


if __name__ == "__main__":
    # Run the server with stdio transport
    mcp.run(transport='stdio')