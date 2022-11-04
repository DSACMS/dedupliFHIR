import os

from flask import Flask

base_dir = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_url_path="/static",
        static_folder="static",
        template_folder="templates",
    )
    app.config["SECRET_KEY"] = "dev"

    from . import views

    app.register_blueprint(views.views)

    return app


if __name__ == "__main__":
    import sys

    app = create_app()

    try:
        port = int(sys.argv[1])
    except (IndexError, ValueError):
        port = 5000
    app.run(debug=True, port=port)
