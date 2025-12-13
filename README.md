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
Run the script to download and parse your bills :
```
python main.py
```
I just trivially save the corresponding pdf passwords in `password.json` like :
```
{"CBG": CBG_PASSWORD, "TSB": TSB_PASSWORD, ...}
```
and read them by :
```
   with open("password.json", "r") as f:
         passwords = json.load(f)
   if filename.startswith("CBG"):
         password = passwords["CBG"]
   elif filename.startswith("TSB"):
         password = passwords["TSB"]
```
so you might need to take care them by yourself.

After running `main.py`, the parsed bills will be saved in the `bill/` folder, organized by month (e.g., `bills_11.txt`).

You can then chat with ChatGPT about a specific month's bill. Make sure you get the api key from ChatGPT, by following the OpenAI [instructions](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key),
and put it into `chat_key.txt` then run :
```
python chat.py
```
The script will prompt you to select a month (e.g., enter `11` for November). The assistant will get the bill contents for that month.

The conversation will be automatically recorded in the `chat/` folder (e.g., `chat/chat_11.txt`).
