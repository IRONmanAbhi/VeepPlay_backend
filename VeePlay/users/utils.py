from flask import url_for, current_app
from VeePlay import mail
import secrets
import os
from PIL import Image
from flask_mail import Message


def savePicture(form_picture, old_name):
    if old_name != "default.jpg":
        picPath = os.path.join(current_app.root_path, "static/profile_pics", old_name)
        if os.path.exists(picPath):
            os.remove(picPath)

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    new_name = random_hex + f_ext
    pic_path = os.path.join(current_app.root_path, "static/profile_pics", new_name)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(pic_path)
    return new_name


def send_reset_emails(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request", sender="noreply@gmail.com", recipients=[user.email]
    )
    msg.body = f"""Dear {user.username},

We have received a request to reset the password for your account. Please follow the instructions below to reset your password:

Click on the link below to reset your password: {url_for("users.reset_password", token=token, _external=True)}

Note: This link will expire in 15 minutes for security purposes.

After clicking the link, you will be prompted to set a new password. Please enter your new password, confirm it, and submit the form.

If you did not request a password reset, please ignore this email, and your account will remain secure.

Best regards,
Developers
VeePlay
"""
    mail.send(msg)
