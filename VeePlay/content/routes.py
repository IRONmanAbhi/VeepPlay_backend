from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from VeePlay.models import db, Content, Season, Episode, WatchHistory
from VeePlay.content.utils import generate_presigned_url

content = Blueprint("content", __name__)


@content.route("/shows", methods=["GET"])
def get_all_shows():
    shows = Content.query.filter_by(type="S").all()
    result = [
        {
            "name": show.name,
            "description": show.description,
            "poster": generate_presigned_url(show.poster),
            "trailer": generate_presigned_url(show.trailer),
            "genre": show.genre,
        }
        for show in shows
    ]
    return jsonify(result), 200


@content.route("/movies", methods=["GET"])
def get_all_movies():
    movies = Content.query.filter_by(type="M").all()
    result = [
        {
            "name": movie.name,
            "description": movie.description,
            "poster": generate_presigned_url(movie.poster),
            "trailer": generate_presigned_url(movie.trailer),
            "genre": movie.genre,
        }
        for movie in movies
    ]
    return jsonify(result), 200


@content.route("/shows/<string:show_name>", methods=["GET"])
def get_show_details(show_name):
    show = Content.query.filter_by(name=show_name, type="S").first()
    if not show:
        return jsonify({"message": "Show not found"}), 404

    seasons = [
        {
            "season_number": season.season_number,
            "episodes": [
                {
                    "episode_no": ep.episode_no,
                    "title": ep.title,
                    "description": ep.description,
                    "thumbnail": generate_presigned_url(ep.thumbnail_path),
                    "video_url": generate_presigned_url(ep.s3_path),
                }
                for ep in season.episodes
            ],
        }
        for season in show.seasons
    ]

    return (
        jsonify(
            {
                "name": show.name,
                "description": show.description,
                "trailer": generate_presigned_url(show.trailer),
                "poster": generate_presigned_url(show.poster),
                "genre": show.genre,
                "seasons": seasons,
            }
        ),
        200,
    )


@content.route("/movies/<string:movie_name>", methods=["GET"])
def get_movie_details(movie_name):
    movie = Content.query.filter_by(name=movie_name, type="M").first()
    if not movie:
        return jsonify({"message": "Movie not found"}), 404

    video = movie.movie_video
    return (
        jsonify(
            {
                "name": movie.name,
                "description": movie.description,
                "trailer": generate_presigned_url(movie.trailer),
                "poster": generate_presigned_url(movie.poster),
                "genre": movie.genre,
                "video": {
                    "s3_path": generate_presigned_url(video.s3_path) if video else None,
                    "thumbnail_path": (
                        generate_presigned_url(video.thumbnail_path) if video else None
                    ),
                    "duration": video.duration if video else None,
                },
            }
        ),
        200,
    )


@content.route("/movies/<string:movie_name>/video", methods=["GET"])
@jwt_required()
def get_movie_video(movie_name):
    movie = Content.query.filter_by(name=movie_name, type="M").first()
    if not movie or not movie.movie_video:
        return jsonify({"message": "Video not found"}), 404

    video = movie.movie_video

    signed_url = generate_presigned_url(video.s3_path)

    signed_thumbnail = (
        generate_presigned_url(video.thumbnail_path) if video.thumbnail_path else None
    )

    return (
        jsonify(
            {
                "s3_path": signed_url,
                "thumbnail_path": signed_thumbnail,
                "duration": video.duration,
            }
        ),
        200,
    )


@content.route(
    "/shows/<string:show_name>/<int:season_number>/<int:episode_number>",
    methods=["GET"],
)
@jwt_required()
def get_episode(show_name, season_number, episode_number):
    show = Content.query.filter_by(name=show_name, type="S").first()
    if not show:
        return jsonify({"message": "Show not found"}), 404

    season = Season.query.filter_by(
        content_id=show.id, season_number=season_number
    ).first()
    if not season:
        return jsonify({"message": "Season not found"}), 404

    episode = Episode.query.filter_by(
        season_id=season.id, episode_no=episode_number
    ).first()
    if not episode:
        return jsonify({"message": "Episode not found"}), 404
    return (
        jsonify(
            {
                "show_id": show.id,
                "title": str(episode.title),
                "description": str(episode.description),
                "s3_path": generate_presigned_url(episode.s3_path),
                "thumbnail_path": generate_presigned_url(episode.thumbnail_path),
                "duration": episode.duration,
            }
        ),
        200,
    )


@content.route("/continue-watching", methods=["GET"])
@jwt_required()
def continue_watching():
    user_email = get_jwt_identity()

    history = (
        db.session.query(WatchHistory)
        .join(Content, WatchHistory.content_id == Content.id)
        .filter(WatchHistory.user_email == user_email)
        .order_by(WatchHistory.last_watched.desc())
        .limit(10)
        .all()
    )

    results = []
    for entry in history:
        results.append(
            {
                "content_id": entry.content.id,
                "title": entry.content.title,
                "type": entry.content.type,
                "genre": entry.content.genre,
                "thumbnail": generate_presigned_url(entry.content.thumbnail),
                "last_watched": entry.last_watched.isoformat(),
            }
        )

    return jsonify(results), 200


@content.route("/watch_history", methods=["POST"])
@jwt_required()
def update_watch_history():
    user_id = get_jwt_identity()
    data = request.get_json()
    content_id = data.get("content_id")
    progress = data.get("progress", 0)

    history = WatchHistory.query.filter_by(
        user_id=user_id, content_id=content_id
    ).first()

    if history:
        history.progress = progress
    else:
        history = WatchHistory(
            user_id=user_id, content_id=content_id, progress=progress
        )
        db.session.add(history)

    db.session.commit()
    return jsonify({"message": "Watch history updated"}), 200


@content.route("/search")
def search_content():
    query = request.args.get("q", "").strip().lower()

    if not query:
        return jsonify({"message": 'Query parameter "q" is required'}), 400

    matched_content = Content.query.filter(Content.name.ilike(f"%{query}%")).all()

    results = {"movies": [], "shows": []}

    for item in matched_content:
        content_data = {
            "name": item.name,
            "genre": item.genre,
            "description": item.description,
            "poster": generate_presigned_url(item.poster),
            "trailer": generate_presigned_url(item.trailer),
        }
        if item.type == "M":
            results["movies"].append(content_data)
        elif item.type == "S":
            results["shows"].append(content_data)

    return jsonify(results), 200


@content.route("/filter")
def filter_by_genre():
    genre = request.args.get("genre", "").strip().lower()
    if not genre:
        return jsonify({"message": "Genre parameter is required"}), 400

    filtered_content = Content.query.filter(Content.genre.any(genre)).all()
    movies = [
        {"name": c.name, "genre": c.genre} for c in filtered_content if c.type == "M"
    ]
    shows = [
        {"name": c.name, "genre": c.genre} for c in filtered_content if c.type == "S"
    ]

    return jsonify({"movies": movies, "shows": shows}), 200
