import os
from core.services.llm import LLMService

BILL_DIR = "bill"

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

def send_initial(llm: LLMService, bill: str):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant who can answer questions about the user's credit card bill.",
        },
    ]

    if bill:
        input_text = f"Here is my credit card bill:\n{bill}, reply me if you received it."
        messages.append({"role": "user", "content": input_text})
        
        reply = llm.chat(messages)
        print(f"Assistant: {reply}")
        messages.append({"role": "assistant", "content": reply})

    return messages

def chat_loop(llm: LLMService, messages, log_file=None):
    """Simple CLI interaction loop."""
    
    # Log initial history
    if log_file:
        with open(log_file, "w", encoding="utf-8") as f:
            for message in messages:
                f.write(f"{message['role']}: {message['content']}\n")

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

        messages.append({"role": "user", "content": user_input})
        
        reply = llm.chat(messages)
        print(f"Assistant: {reply}")
        messages.append({"role": "assistant", "content": reply})
        
        if log_file:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"assistant: {reply}\n")

def run_chat():
    bill, month = load_bill()
    if not bill:
        return
        
    # Ensure chat directory exists
    chat_dir = "chat"
    if not os.path.exists(chat_dir):
        os.makedirs(chat_dir)
        
    log_file = os.path.join(chat_dir, f"chat_{month}.txt")
    print(f"Conversation will be recorded to {log_file}")
    
    llm = LLMService()
    history = send_initial(llm, bill)
    chat_loop(llm, history, log_file)
