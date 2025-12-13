# Mercurius
Parse my credit card bills from Gmail and let ChatGPT tell me what I want to know.

# Environment Setup
## Gmail API Setup
 
To use this project, you need to enable the Gmail API and set up credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Enable the Gmail API for your project.
4. In "APIs & Services" > "Credentials", create OAuth client ID credentials:
   - Application type: Desktop app
   - Download the `credentials.json` file and place it in the project directory.
5. The first time you run the script, it will prompt you to log in with your Google account and authorize access. This will create a `token.json` file for future use.

For more details, see the [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python).

## Dependency
Install the Gmail API dependency with:
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
and pypdf
```
pip install pypdf cryptography>=3.1
```
and the OpenAI client
```
pip install openai
```

## Usage
## Usage

### Bill Analyzer
The project now uses a unified CLI.

1. **Download Bills**:
   ```
   python main.py bills download
   ```
   Downloads PDF attachments from Gmail to `attachments/`.

2. **Parse Bills**:
   ```
   python main.py bills parse
   ```
   Decrypts and parses PDFs into `bill/` folder (e.g., `bills_11.txt`).

3. **Chat with Bills**:
   ```
   python main.py bills chat
   ```
   Select a month and chat with the assistant about your expenses.
   Conversations are recorded in `chat/`.

### Newsletter Sweeper (Web API)
To run the web server for email management:
```
python main.py server
```
The API will be available at `http://localhost:8000`.
Docs: `http://localhost:8000/docs`
