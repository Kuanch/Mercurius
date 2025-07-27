import os
import openai

PARSED_FILE = "parsed.txt"


def load_bill(path=PARSED_FILE) -> str:
    """Return the content of the parsed credit card bill if available."""
    if not os.path.exists(path):
        print(f"Could not find {path}, continuing without initial context.")
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def init_openai() -> None:
    """Configure the OpenAI client using the environment variable."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")
    openai.api_key = api_key


def send_initial(bill: str):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant who can answer questions about the user's credit card bill.",
        },
    ]

    if bill:
        messages.append({"role": "user", "content": f"Here is my credit card bill:\n{bill}"})
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        reply = response.choices[0].message.content
        print(reply)
        messages.append({"role": "assistant", "content": reply})

    return messages


def chat_loop(messages):
    """Simple CLI interaction loop."""
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
        messages.append({"role": "user", "content": user_input})
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        reply = response.choices[0].message.content
        print(f"Assistant: {reply}")
        messages.append({"role": "assistant", "content": reply})


def main():
    init_openai()
    bill = load_bill()
    history = send_initial(bill)
    chat_loop(history)


if __name__ == "__main__":
    main()
