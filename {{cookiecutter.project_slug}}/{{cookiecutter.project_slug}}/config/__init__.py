import glob
import os


def import_env_vars(directory):
    """
    List the files present in the given directory and for each of them create an environment variable named after the
    file, and which value is the contents of the file.
    """
    env_vars = glob.glob(os.path.join(directory, "*"))

    for env_var in env_vars:
        with open(env_var, "r") as env_var_file:
            os.environ.setdefault(
                env_var.split(os.sep)[-1], env_var_file.read().strip()
            )


def get_project_root_path():
    """
    Return the absolute path to the root of the project.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
