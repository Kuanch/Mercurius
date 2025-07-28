import os
import pdb
import openai

PARSED_FILE = "parsed.txt"


def load_bill(path=PARSED_FILE) -> str:
    """Return the content of the parsed credit card bill if available."""
    if not os.path.exists(path):
        print(f"Could not find {path}, continuing without initial context.")
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_openai_key() -> None:
    """Configure the OpenAI client using the environment variable."""
    with open("chat_key.txt", "r") as f:
        api_key = f.read().strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")
    return api_key


def send_initial(bill: str):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant who can answer questions about the user's credit card bill.",
        },
    ]
    key = get_openai_key()

    if bill:
        client = openai.OpenAI(api_key=key)

        input_text = f"Here is my credit card bill:\n{bill}, reply me if you received it."
        messages.append({"role": "user", "content": input_text})
        response = client.responses.create(
            model="gpt-4.1",
            input=input_text
        )
        reply = response.output[0].content[0].text
        print(f"Assistant: {reply}")
        messages.append({"role": "assistant", "content": reply})

    return client, messages


def chat_loop(client, messages):
    """Simple CLI interaction loop."""
    input_text = ""
    for message in messages:
        input_text += f"{message['role']}: {message['content']}\n"
    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit"}:
            break
        input_text += f"user: {user_input}\n"
        response = client.responses.create(
                    model="gpt-4.1",
                    input=input_text,
        )
        reply = response.output[0].content[0].text
        print(f"Assistant: {reply}")
        input_text += f"assistant: {reply}\n"


def main():
    bill = load_bill()
    client, history = send_initial(bill)
    chat_loop(client, history)


if __name__ == "__main__":
    main()
