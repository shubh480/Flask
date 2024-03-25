from app import app, models
from flask import jsonify, Response


@app.route("/messages/all", methods=["GET"])
def get_messages() -> Response:
    """
    Find and return a user by their ID.
    :param user_id: Requested user identifier.
    :return:        JSON object of the requested user.
    """
    result = models.Message.query.all()
    messages = []
    if result:
        for row in result:
            messages.append({
                'chat_id': row.chat_id,
                'user_id': row.user_id,
                'text': row.text,
                'sent_at': row.sent_at
            })

    return jsonify(messages)