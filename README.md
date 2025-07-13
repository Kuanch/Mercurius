# Mercurius
Parse my mails and tell me what I want to know.

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
Install the dependency with:
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Usage
Run the script:
```
python main.py
```
