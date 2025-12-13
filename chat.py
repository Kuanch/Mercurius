import os
import pdb
import openai

BILL_DIR = "bill"
GPT_MODEL = "o3" # Change to any listed here: https://platform.openai.com/docs/pricing


def select_bill() -> tuple[str, str]:
    """List available bills and let the user select one."""
    if not os.path.exists(BILL_DIR):
        print(f"Directory {BILL_DIR} does not exist.")
        return "", ""
    
    files = [f for f in os.listdir(BILL_DIR) if f.startswith("bills_") and f.endswith(".txt")]
    files.sort()
    
    if not files:
        print(f"No bill files found in {BILL_DIR}.")
        return "", ""
        
    print("Available bills:")
    months = []
    for f in files:
        # Extract month from bills_XX.txt
        month = f.split("_")[1].split(".")[0]
        months.append(month)
        print(f" - {month}")
        
    while True:
        selection = input("Select month (e.g. 11): ").strip()
        if selection in months:
            return os.path.join(BILL_DIR, f"bills_{selection}.txt"), selection
        print("Invalid selection. Please try again.")

def load_bill() -> tuple[str, str]:
    """Return the content of the parsed credit card bill if available."""
    path, month = select_bill()
    if not path:
        return "", ""
        
    print(f"Loading bill from {path}...")
    with open(path, "r", encoding="utf-8") as f:
        return f.read(), month


def get_openai_key() -> None:
    """Configure the OpenAI client using the environment variable."""
    with open("chat_key.txt", "r") as f:
        api_key = f.read().strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")
    return api_key


def find_content(response) -> str:
    """Extract content from text between start and end markers."""
    for output in response.output:
        if hasattr(output, 'content'):
            return output.content[0].text
    raise ValueError(f"No content found in the response, response: {response}")


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
            model=GPT_MODEL,
            input=input_text
        )
        # WTF?
        reply = find_content(response)
        print(f"Assistant: {reply}")
        messages.append({"role": "assistant", "content": reply})

    return client, messages


def chat_loop(client, messages, log_file=None):
    """Simple CLI interaction loop."""
    input_text = ""
    
    # Log initial history
    if log_file:
        with open(log_file, "w", encoding="utf-8") as f:
            for message in messages:
                f.write(f"{message['role']}: {message['content']}\n")

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
            
        if log_file:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"user: {user_input}\n")

        input_text += f"user: {user_input}\n"
        response = client.responses.create(
                    model=GPT_MODEL,
                    input=input_text,
        )
        reply = find_content(response)
        print(f"Assistant: {reply}")
        
        if log_file:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"assistant: {reply}\n")

        input_text += f"assistant: {reply}\n"


def main():
    bill, month = load_bill()
    if not bill:
        return
        
    # Ensure chat directory exists
    chat_dir = "chat"
    if not os.path.exists(chat_dir):
        os.makedirs(chat_dir)
        
    log_file = os.path.join(chat_dir, f"chat_{month}.txt")
    print(f"Conversation will be recorded to {log_file}")
    
    client, history = send_initial(bill)
    chat_loop(client, history, log_file)


if __name__ == "__main__":
    main()
