from app import app, models
from flask import jsonify, Response
from sqlalchemy import func

from app.models import User, Chat

# TODO: Give the route a name/path.
@app.route("/users/stats", methods=["GET"])
def get_users_performance() -> Response:
    """
    Return the interactions completed and average handling time of every user.
    :return: JSON array:

    [
        {
            "userId": 1,
            "name": "Test User",
            "chatsHandled": 10,
            "averageHandlingSeconds": 120
        },
        ...
    ]

    """

    
    # Query for taking the performance statistics from User and Chat table
    result = models.User.query \
    .outerjoin(Chat, User.user_id==Chat.user_id) \
    .with_entities(User.user_id.label('user_id'), User.name.label('name'), func.count().label('total'), func.avg((func.strftime('%s', Chat.handle_end) - func.strftime('%s', Chat.handle_start))).label('time')) \
    .group_by(User.user_id).all()
    
    # Preparing the records for returning
    user_stat = serialize_user_stats(result)

    return jsonify(user_stat)


def serialize_user_stats(result: list) -> list[dict]:
    performances = []
    for row in result:
        avg_time = row.time
        total_chat = row.total
        if avg_time == None:
            avg_time = 0
            total_chat = 0

        performances.append({
            "userId": row.user_id,
            "name": row.name,
            "chatsHandled": total_chat,
            "averagehandlingSeconds": avg_time
        })

    return performances