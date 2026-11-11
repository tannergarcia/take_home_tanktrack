from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from .config import Config
from .db import db


def create_app(config_object=None):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_object or Config)
    db.init_app(app)

    from .api.errors import register_error_handlers
    from .api.jobs import jobs_bp
    from .api.technicians import technicians_bp
    from .seed import register_seed_command, seed_if_empty

    app.register_blueprint(jobs_bp, url_prefix="/api")
    app.register_blueprint(technicians_bp, url_prefix="/api")
    register_error_handlers(app)
    register_seed_command(app)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/", defaults={"path": ""})
    @app.get("/<path:path>")
    def frontend(path):
        dist = Path(app.root_path).parent / "frontend" / "dist"
        requested = dist / path
        if path and requested.is_file():
            return send_from_directory(dist, path)
        if (dist / "index.html").is_file():
            return send_from_directory(dist, "index.html")
        return jsonify({"message": "Frontend has not been built"}), 404

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()
        if app.config.get("SEED_ON_START", True):
            seed_if_empty()
    return app
