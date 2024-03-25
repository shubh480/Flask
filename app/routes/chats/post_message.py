from http import HTTPStatus
from typing import Tuple
import re
from werkzeug.exceptions import NotFound

from app import app, database
from flask import request

from app.models import Chat, Message


@app.route("/chats/<int:chat_id>/messages", methods=["POST"])
def post_message(chat_id: int) -> Tuple[str, int]:
    """
    Store a message. A message should be rejected if:

        - The chat hasn't started yet.
        - The chat is already finished.
        - The user on the message is not handling the chat.
        - The message is more than 500 characters.

    Credit cards should also be blanked out with asterisks before storage.

    :param chat_id: Store a message for a chat
    """
    try:
        # Getting Chat information
        chat: Chat = Chat.query.get_or_404(chat_id)

        # Retrieving text message from the post request
        text = request.json.get("text")
        
        # Checking if chat session has ended already
        if chat.handle_end is not None:
            return "Can't store a message after the chat has ended.", HTTPStatus.BAD_REQUEST

        # Checking if message has more than 500 characters
        if _is_too_long(text):
            return "The message cannot be more than 500 characters.", HTTPStatus.BAD_REQUEST

        # Checking if user is assosiated with the Chat
        user_id = None
        if "user_id" in request.json:
            user_id = request.json.get('user_id')
            if not _is_handling_agent(chat, user_id):
                return "That agent isn't handling the chat.", HTTPStatus.BAD_REQUEST

        # Striping sensition text like credit card with *
        text = _strip_sensitive_text(text)

        # Store the message.
        if user_id:
            message = Message(chat_id=chat.chat_id, text=text, user_id=user_id)
        else:
            message = Message(chat_id=chat.chat_id, text=text)

        database.session.add(message)
        database.session.commit()
        
        return "Message added successfully.", HTTPStatus.CREATED

    except NotFound as e:
        return "Can't store a message before the chat has started.", HTTPStatus.BAD_REQUEST


def _is_handling_agent(chat: Chat, user_id) -> bool:
    """
    If the message has a user ID, it has to match the agent of the chat.
    :param chat:    Chat being updated.
    :param message: Message being stored.
    :return:        True if the agent is correct or False otherwise.
    """
    if user_id != chat.user_id:
        return False

    return True


def _is_too_long(text: str) -> bool:
    """
    Don't store messages that are too long.
    :param chat: Chat being updated.
    :return:     True if the message is too long.
    """

    return len(text) > 500


def _strip_sensitive_text(text: str) -> bool:
    """
    Remove credit card numbers.
    :param text: Message text.
    """
    # Regular expression
    return re.sub(r"\d{4} \d{4} \d{4} \d{4}", lambda match: '*' * len(match.group()), text)
