# part4/ui.py

import gradio as gr
import aiohttp
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ui.log'
)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000"


class ChatState:
    def __init__(self):
        self.messages = []
        self.user_info = {}
        self.phase = "collect_info"  # or "qa"


async def send_chat_message(message, history, state):
    """Send a message to the chat endpoint."""
    try:
        logger.info(f"Processing chat message: {message}")
        state.messages.append({"role": "user", "content": message})

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/collect_info",
                json={"messages": state.messages}
            ) as response:

                if response.status == 200:
                    reply = (await response.json())["response"]
                    state.messages.append({"role": "assistant", "content": reply})

                    med_options = ["כללית", "מכבי", "מאוחדת", "clalit", "maccabi", "meuhedet"]
                    if message.lower() in med_options:
                        state.user_info["hmo"] = message.lower()
                        logger.info(f"Updated HMO info: {message.lower()}")

                    ab_options = ["זהב", "כסף", "ארד", "gold", "silver", "bronze"]
                    if message.lower() in ab_options:
                        state.user_info["tier"] = message.lower()
                        state.phase = "qa"
                        logger.info(f"Updated tier info: {message.lower()}, switching to QA phase")

                    updated_history = history + [
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": reply},
                    ]
                    logger.info("Successfully processed chat message")
                    return updated_history, state

                error_msg = f"Error: {await response.text()}"
                logger.error(f"Server error: {error_msg}")
                raise Exception(error_msg)

    except Exception as e:
        logger.error(f"Error in send_chat_message: {str(e)}", exc_info=True)
        error_msg = f"Error: {str(e)}"
        updated_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": error_msg},
        ]
        return updated_history, state


async def send_question(message, history, state):
    """Send a question to the QA endpoint."""
    try:
        logger.info(f"Processing question: {message}")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/ask",
                json={
                    "user_info": state.user_info,
                    "question": message
                }
            ) as response:

                if response.status == 200:
                    reply = (await response.json())["answer"]
                    logger.info("Successfully received answer")

                    updated_history = history + [
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": reply},
                    ]
                    return updated_history, state

                error_msg = f"Error: {await response.text()}"
                logger.error(f"Server error: {error_msg}")
                raise Exception(error_msg)

    except Exception as e:
        logger.error(f"Error in send_question: {str(e)}", exc_info=True)
        error_msg = f"Error: {str(e)}"
        updated_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": error_msg},
        ]
        return updated_history, state


async def chat_with_bot(message, history, state):
    """Handle chat interaction based on current phase."""
    try:
        logger.info(f"Chat phase: {state.phase}")
        if state.phase == "collect_info":
            return await send_chat_message(message, history, state)
        else:
            return await send_question(message, history, state)
    except Exception as e:
        logger.error(f"Error in chat_with_bot: {str(e)}", exc_info=True)
        error_msg = f"Error: {str(e)}"
        return history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": error_msg},
        ], state


def reset_chat(state):
    """Reset the chat state."""
    try:
        logger.info("Resetting chat state")
        state.messages = []
        state.user_info = {}
        state.phase = "collect_info"
        logger.info("Chat state reset successfully")
        return [], state
    except Exception as e:
        logger.error(f"Error in reset_chat: {str(e)}", exc_info=True)
        raise


# Create the Gradio interface
with gr.Blocks(title="Health Insurance Chatbot") as demo:
    gr.Markdown("# 🏥 Health Insurance Chatbot | צ'אטבוט לקופות חולים")

    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(
                type="messages",
                label="Chat",
                height=600,
                show_copy_button=True,
                elem_id="chatbot"
            )
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Type your message here... | הקלד כאן את ההודעה שלך...",
                    show_label=False,
                    container=False
                )
                submit = gr.Button("Send | שלח", variant="primary")

        with gr.Column(scale=1):
            reset_btn = gr.Button("Reset Chat | איפוס צ'אט", variant="secondary")

    chatbot_state = gr.State(ChatState())

    # Set up event handlers
    submit.click(chat_with_bot, [msg, chatbot, chatbot_state], [chatbot, chatbot_state]).then(
        lambda: "", None, [msg]
    )
    msg.submit(chat_with_bot, [msg, chatbot, chatbot_state], [chatbot, chatbot_state]).then(
        lambda: "", None, [msg]
    )
    reset_btn.click(reset_chat, [chatbot_state], [chatbot, chatbot_state])

# Launch the interface
if __name__ == "__main__":
    try:
        logger.info("Starting UI application")
        demo.launch()
        logger.info("UI application launched successfully")
    except Exception as e:
        logger.error(f"Error launching UI: {str(e)}", exc_info=True)
        raise
