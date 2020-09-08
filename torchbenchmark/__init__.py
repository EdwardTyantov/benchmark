import os
from pathlib import Path
import subprocess
import sys
import torch
from urllib import request
proxy_suggestion = "Unable to verify https connectivity, " \
                   "required for setup.\n" \
                   "Do you need to use a proxy?"

this_dir = Path(__file__).parent.absolute()
model_dir = 'models'
install_file = 'install.py'


def _test_https(test_url='https://github.com', timeout=0.5):
    try:
        request.urlopen(test_url, timeout=timeout)
    except OSError:
        return False
    return True


def _install_deps(model_path):
    if os.path.exists(os.path.join(model_path, install_file)):
        subprocess.check_call([sys.executable, install_file], cwd=model_path)
    else:
        print('No install.py is found in {}.'.format(model_path))
        sys.exit(-1)


class workdir():
    def __init__(self, path):
        self.path = path
        self.cwd = os.getcwd()

    def __enter__(self):
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.cwd)


def list_model_paths():
    p = Path(__file__).parent.joinpath(model_dir)
    return sorted(str(child.absolute()) for child in p.iterdir() if child.is_dir())


def setup():
    if not _test_https():
        print(proxy_suggestion)
        sys.exit(-1)

    for model_path in list_model_paths():
        _install_deps(model_path)


def list_models():
    models = []
    for model_path in list_model_paths():
        model_name = os.path.basename(model_path)
        module = importlib.import_module(f'.models.{model_name}', package=__name__)
        print(dir(module), module.__file__)
        Model = getattr(module, 'Model')
        models.append(Model)
    return zip(models, list_model_paths())
