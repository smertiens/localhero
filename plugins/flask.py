from ._base import BasePlugin

class FlaskPlugin(BasePlugin):
    
    handles = ['flask']
    server_conf = None

    def __init__(self, server_conf):
        self.server_conf = server_conf

    def get_command(self):
        port = self.server_conf.get('port', 5000)
        cmd = 'flask run --port %s' % (port)
        return cmd

    def before_run(self):
        pass
