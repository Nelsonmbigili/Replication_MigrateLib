import cherrypy
from alchemical.cherrypy import Alchemical
from config import Config

db = Alchemical()


class MyApp:
    def __init__(self, config_class=Config):
        self.config = config_class
        self.init_extensions()

    def init_extensions(self):
        # Initialize the database
        db.init_app(self)

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/apifairy/docs")

    @staticmethod
    def start_server():
        # CherryPy server configuration
        cherrypy.config.update({
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 8080,
            'engine.autoreload.on': False,
        })

        # Mount the application
        cherrypy.quickstart(MyApp())


# Start the CherryPy server
if __name__ == "__main__":
    MyApp.start_server()
