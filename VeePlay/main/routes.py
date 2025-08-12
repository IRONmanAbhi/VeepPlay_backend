from flask import Blueprint, jsonify
from VeePlay.models import Content

main = Blueprint("main", __name__)


def serialize_video(video):
    return {
        "id": video.id,
        "s3_path": video.s3_path,
        "thumbnail_url": video.thumbnail_url,
        "duration": video.duration,
        "trailer_url": video.trailer_url,
    }


def serialize_episode(episode):
    return {
        "id": episode.id,
        "title": episode.title,
        "description": episode.description,
        "episode_no": episode.episode_no,
        "video": serialize_video(episode.video) if episode.video else None,
    }


def serialize_season(season):
    return {
        "id": season.id,
        "season_number": season.season_number,
        "episodes": [serialize_episode(e) for e in season.episodes],
    }


def serialize_content(content):
    return {
        "id": content.id,
        "name": content.name,
        "description": content.description,
        "type": content.type,
        "banner": content.banner,
        "language": content.language,
        "category": content.category,
        "thumbnail": content.thumbnail,
        "release_date": content.release_date.strftime("%Y-%m-%d"),
        "seasons": (
            [serialize_season(s) for s in content.seasons]
            if content.type == "show"
            else []
        ),
        "video": (
            serialize_video(content.video)
            if content.type == "movie" and content.video
            else None
        ),
    }


@main.route("/")
@main.route("/home")
def home():
    contents = Content.query.all()
    return (
        jsonify(
            {"status": "success", "contents": [serialize_content(c) for c in contents]}
        ),
        200,
    )


@main.route("/about")
def about():
    return (
        jsonify(
            {
                "status": "success",
                "message": "Welcome to VeePlay — Your OTT Streaming Backend API",
                "routes": [
                    "POST   /register                            - Register a new user",
                    "POST   /login                               - Login and get JWT token",
                    "GET    /account                             - Get current user's account details",
                    "PUT    /account/<email>                     - Edit user account by email",
                    "POST   /forgot-password                     - Send password reset link",
                    "POST   /reset-password/<token>              - Reset password using token",
                    "GET    /shows                               - List all shows",
                    "GET    /movies                              - List all movies",
                    "GET    /shows/<show_name>                   - Get details of a specific show",
                    "GET    /movies/<movie_name>                 - Get details of a specific movie",
                    "GET    /movies/<movie_name>/video           - Get video for a movie (requires auth)",
                    "GET    /shows/<show>/<season>/<episode>     - Get a specific episode (requires auth)",
                    "GET    /continue-watching                   - Get user's continue watching list (requires auth)",
                    "POST   /watch_history                       - Update watch history (requires auth)",
                    "GET    /search?q=query                      - Search content by name",
                    "GET    /filter?genre=genre                  - Filter content by genre",
                    "GET    /                                     - Homepage with all content",
                    "GET    /home                                 - Same as /",
                    "GET    /about                                - About this API and route listing",
                ],
            }
        ),
        200,
    )
