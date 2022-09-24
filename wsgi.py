from flask import Flask

"""Initialize Flask app."""
def init_app():
    """Construct core Flask application with embedded Dash app."""

    app = Flask(__name__,
                  instance_relative_config=False,
                  static_url_path="/interface/static",
                  static_folder='interface/static',
                  template_folder='interface/templates'
                  )

    with app.app_context():
        from api import resources
        from interface import routes

        from interface.views.dashboard import init_dashboard

        app = init_dashboard(app)

        return app


app = init_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=80)
