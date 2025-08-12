from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from VeePlay.models import User, WatchHistory, UsedTokens
from VeePlay import mail, db, bcrypt
from VeePlay.users.utils import savePicture, send_reset_emails

users = Blueprint("users", __name__)


@users.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 409

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        username=username, email=email, img_file="default.jpg", password=hashed_pw
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201


@users.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    return (
        jsonify(
            {"token": access_token, "username": user.username, "email": user.email}
        ),
        200,
    )


@users.route("/account", methods=["GET"])
@jwt_required()
def account_details():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    history = WatchHistory.query.filter_by(user_id=user.id).all()
    history_data = []
    for entry in history:
        content = entry.content
        history_data.append(
            {
                "content_id": content.id,
                "content_name": content.name,
                "content_type": content.type,
                "poster": content.poster,
                "progress": entry.progress,
            }
        )

    return (
        jsonify(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "img_file": user.img_file,
                "watch_history": history_data,
            }
        ),
        200,
    )


@users.route("/account/<string:email>", methods=["PUT"])
@jwt_required()
def edit_info(email):
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.id != current_user_id:
        return jsonify({"message": "Unauthorized"}), 403

    old_img_file = user.img_file

    new_username = request.form.get("username")
    new_email = request.form.get("email")
    new_img_file = request.files.get("img_file")

    if new_email and new_email != user.email:
        if User.query.filter_by(email=new_email).first():
            return jsonify({"message": "Email already in use"}), 409
        user.email = new_email

    if new_username:
        user.username = new_username

    if new_img_file:
        new_img = savePicture(new_img_file, old_img_file)
        user.img_file = new_img

    db.session.commit()

    return (
        jsonify(
            {
                "message": "User updated successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "img_file": user.img_file,
                },
            }
        ),
        200,
    )


@users.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Email not found"}), 404

    send_reset_emails(user)

    return jsonify({"message": "Reset link sent to email"}), 200


@users.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    user = User.verify_reset_token(token)

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    new_password = data.get("password")
    user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    db.session.commit()

    newToken = UsedTokens(usedToken=token)
    db.session.add(newToken)
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200
