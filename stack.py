import yaml
import os, time
import logging
import subprocess, threading, psutil, signal
from plugins import flask, npm


def process_variables(s: str, vars: dict) -> str:
    # TODO: proper regex?
    for k, v in vars.items():
        s = s.replace('$'+k, v)
    
    return s

class ServerConfig:

    data = {}

    def __init__(self, data):
        self.data = data

    def get(self, k, d = None)->any:
        if k in self.data:
            return self.data[k]
        else:
            return d

class Config:

    servers = {}

    def __init__(self):
        self.servers = {}
    
    @staticmethod
    def get_config_file():
        f = os.path.realpath(os.path.join(os.path.dirname(__file__), 'config.yaml'))

        if os.path.exists(f):
            return f
        else:
            raise IOError('Config file "%s" not found' % f)

    def load_yaml(self, filename: str):
        
        with open(filename, 'r') as fp:
            try:
                servers = yaml.load(fp, Loader=yaml.SafeLoader)['servers']

                for name, conf in servers.items():
                    self.servers[name] = ServerConfig(conf)

            except Exception as e:
                raise Exception('Could not load config file "%s": %s' % (filename, str(e)))


    def get_servers(self) -> dict:
        return self.servers

class ServerRunnerEnvironment:

    plugins = []

    def __init__(self):
        self.plugins = [flask.FlaskPlugin, npm.NPMPlugin]


class ServerRunner(threading.Thread):

    conf = None
    env = None
    cmd = ''
    output = []
    process_id = None
    name = ''
    logger = None

    def __init__(self, conf: ServerConfig, env: ServerRunnerEnvironment, name = 'Unnamed'):
        super().__init__()

        self.conf = conf
        self.env = env
        self.name = name

        # Setup logging
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        hdl = logging.StreamHandler()
        hdl.setFormatter(logging.Formatter(fmt='%(levelname)s:%(name)s:%(message)s'))
        self.logger.addHandler(logging.StreamHandler())

    def run(self):

        cmd = ''
        found_plugin = False

        # find plugin to handle the config
        for plugin in self.env.plugins:
            if self.conf.get('type', '') in plugin.handles:
                self.logger.info('Using "%s" for type "%s"' % (plugin, self.conf.get('type')))
                plugin_inst = plugin(self.conf)
                cmd = plugin_inst.get_command()

                # stop looking for plugin
                found_plugin = True
                break

        if not found_plugin:
            raise Exception('Could not find a plugin to handle type "%s"' % self.conf.get('type'))

        cwd = os.path.realpath(self.conf.get('dir', '.'))

        if self.conf.get('venv', None) is not None:
            venv_dir = process_variables(self.conf.get('venv'), {'dir': cwd})
            venv_dir = os.path.join(venv_dir, 'bin', 'activate')
            cmd = 'source %s && %s' % (venv_dir, cmd)

        
        self.logger.debug('Running command "%s"' % cmd)
       
        proc = subprocess.Popen(
            args=cmd,               # Python doc recommends str arg if shell=True
            shell=True,
            env=self.conf.get('env', {}),
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True               # stdout as text not as byte stream
        )

        self.process_id = proc.pid

        while (res := proc.poll()) is None:
            if (line := proc.stdout.readline()) != '':
                self.output.append(line)

        self.logger.info('Server process stopped.')


# we need a separate function to shutdown the process, since the thread will block on stdout.readline()
def stop_runner(runner: ServerRunner):

    if not runner.is_alive(): return

    try:
        runner.logger.info('Shutting down process...')

        parent = psutil.Process(runner.process_id)
        children = parent.children(recursive=True)

        for child in children:
            child.send_signal(signal.SIGINT)

        gone, alive = psutil.wait_procs(children, timeout=3)

        for still_alive in alive:
            runner.logger.warning('Process %s is still alive, sending KILL signal...' % still_alive)
            sill_alive.kill()

    except psutil.NoSuchProcess:
        runner.logger.error('Could not determine server runner process.')
