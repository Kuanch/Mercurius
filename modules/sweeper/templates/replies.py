def render_template(template_id: str) -> str:
    if template_id == "unsubscribe_zh":
        return "請幫我取消訂閱，謝謝。"
    elif template_id == "unsubscribe_en":
        return "Please unsubscribe me from this list. Thank you."
    elif template_id == "ack_receipt":
        return "Received with thanks."
    return ""
