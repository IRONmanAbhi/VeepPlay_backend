from VeePlay import db, login_manager
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ARRAY
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    img_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.img_file}')"

    def get_reset_token(self, expires_sec=900):
        s = Serializer(current_app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)


class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(1), nullable=False)
    poster = db.Column(db.String(120), nullable=False)
    trailer = db.Column(db.String(120), nullable=False)
    genre = db.Column(ARRAY(db.String), nullable=False)
    movie_video_id = db.Column(db.Integer, db.ForeignKey("video.id"), nullable=True)
    movie_video = db.relationship("Video", foreign_keys=[movie_video_id], uselist=False)
    seasons = db.relationship("Season", backref="content", lazy=True)

    def __repr__(self):
        return f"<Content(name='{self.name}', type='{self.type}')>"


class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season_number = db.Column(db.Integer, nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)
    episodes = db.relationship("Episode", backref="season", lazy=True)

    def __repr__(self):
        return f"<Season(season_number={self.season_number}, content_id={self.content_id})>"


class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    episode_no = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    s3_path = db.Column(db.String(200), nullable=False)
    thumbnail_path = db.Column(db.String(200), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey("season.id"), nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Episode(title='{self.title}', episode_no={self.episode_no}, season_id={self.season_id})>"


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    s3_path = db.Column(db.String(200), nullable=False)
    thumbnail_path = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Integer)

    def __repr__(self):
        return f"<Video(id={self.id}, s3_path='{self.s3_path}')>"


class WatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)
    progress = db.Column(db.Integer, default=0)
    user = db.relationship("User", backref="watch_history")
    content = db.relationship("Content", backref="watch_history")

    def __repr__(self):
        return f"<WatchHistory(user_id={self.user_id}, content_id={self.content_id}, progress={self.progress})>"


class UsedTokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usedToken = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"UsedTokens('{self.token}')"
