import functools
import os
import random
import subprocess
from datetime import datetime
from io import StringIO

import dj_database_url
from dulwich import porcelain
from fabric import task
from fabric.connection import Connection
from invoke import Exit
from invoke.exceptions import UnexpectedExit

ENVIRONMENTS = {
    "prod": {
        "root": "/var/www/{{ cookiecutter.project_slug }}/prod/",
        "host": "root@myhost",
        "pid": "/path/to/uwsgi/pid",
        # You can set settings that will be automatically deployed when running
        # the `bootstrap` command
        "settings": {
            #     'ALLOWED_HOSTS': 'www.myhost.com',
        },
    },
    "dev": {
        "root": "/var/www/{{ cookiecutter.project_slug }}/dev/",
        "host": "root@myhost",
        "pid": "/path/to/uwsgi/pid",
        # You can set settings that will be automatically deployed when running
        # the `bootstrap` command
        "settings": {
            #     'ALLOWED_HOSTS': 'www.myhost.com',
        },
    },
}

project_name = "{{ cookiecutter.project_slug }}"


def remote(task_func):
    """
    Decorate task functions to check for presence of a Connection instance in their context.
    Also pass the Connection instance in argument for convenience.
    """

    @functools.wraps(task_func)
    def call_task_with_connection(ctx, *args, **kwargs):
        if not hasattr(ctx, "conn"):
            raise RuntimeError("Trying to run a remote task with no environment loaded")
        return task_func(ctx, *args, **kwargs)

    return call_task_with_connection


class CustomConnection(Connection):
    """
    Add helpers function on Connection
    """

    @property
    def project_root(self):
        return self.config.root

    @property
    def wwwroot(self):
        """
        Return the path to the root of the project on the remote server.
        """
        return os.path.join(self.project_root, project_name)

    @property
    def venvpath(self):
        return os.path.join(self.project_root, "venv")

    @property
    def envdirpath(self):
        return os.path.join(self.wwwroot, "envdir")

    @property
    def backups_root(self):
        """
        Return the path to the backups directory on the remote server.
        """
        return os.path.join(self.project_root, "backups")

    def run_in_wwwroot(self, cmd, **kwargs):
        """
        Run command after a cd to the wwwroot
        """
        with self.cd(self.wwwroot):
            return self.run(cmd, **kwargs)

    def git(self, gitcmd, **kwargs):
        """
        git from the wwwroot
        """
        return self.run_in_wwwroot("git {}".format(gitcmd), **kwargs)

    def run_in_venv(self, cmd, args, **run_kwargs):
        """
        Binaries from the venv
        """
        return self.run_in_wwwroot(
            "{} {}".format(os.path.join(self.venvpath, "bin", cmd), args), **run_kwargs
        )

    def mk_venv(self, **run_kwargs):
        """
        Create the venv
        """
        return self.run_in_wwwroot(
            "virtualenv --python=/usr/bin/python3 {}".format(self.venvpath),
            **run_kwargs
        )

    def pip(self, args, **run_kwargs):
        """
        pip from the venv, in the wwwroot
        """
        return self.run_in_venv("pip", args, **run_kwargs)

    def python(self, args, **run_kwargs):
        """
        python from the venv, in the wwwroot
        """
        return self.run_in_venv("python", args, **run_kwargs)

    def manage_py(self, args, **run_kwargs):
        """
        manage.py with the python from the venv, in the wwwroot
        """
        env = {}
        try:
            env["DJANGO_SETTINGS_MODULE"] = self.config.settings[
                "DJANGO_SETTINGS_MODULE"
            ]
        except KeyError:
            pass
        return self.python("./manage.py {}".format(args), env=env, **run_kwargs)

    def set_setting(self, name, value=None, force: bool = True):
        """
        Set a setting in the environment directory, for use by Django
        """

        if value is None:
            value = input("Value for {}: ".format(name))

        # Convert booleans into ints, so that Django takes them back easily
        if isinstance(value, bool):
            value = int(value)

        envfile_path = os.path.join(self.envdirpath, name)

        will_write = force
        try:
            # Test that it does exist
            self.run_in_wwwroot("test -r {}".format(envfile_path), hide=True)
        except UnexpectedExit:
            will_write = True

        if will_write:
            self.put(StringIO("{}\n".format(value)), envfile_path)

    def dump_db(self, destination):
        """
        Dump the database to the given directory and return the path to the file created.
        This creates a gzipped SQL file.
        """
        with self.cd(self.wwwroot):
            db_credentials = self.run("cat envdir/DATABASE_URL", hide=True).stdout.strip()
        db_credentials_dict = dj_database_url.parse(db_credentials)

        if not is_supported_db_engine(db_credentials_dict["ENGINE"]):
            raise NotImplementedError(
                "The dump_db task doesn't support the remote database engine"
            )

        outfile = os.path.join(
            destination, datetime.now().strftime("%Y-%m-%d_%H%M%S.sql.gz")
        )

        self.run(
            "pg_dump -O -x -h {host} -U {user} {db}|gzip > {outfile}".format(
                host=db_credentials_dict["HOST"],
                user=db_credentials_dict["USER"],
                db=db_credentials_dict["NAME"],
                outfile=outfile,
            ),
            env={"PGPASSWORD": db_credentials_dict["PASSWORD"].replace("$", "\$")},
        )

        return outfile

    def create_structure(self):
        """
        Create the basic directory structure on the remote server.
        """
        self.run("mkdir -p %s" % self.wwwroot)

        with self.cd(self.project_root):
            self.run("mkdir -p static backups media")
            self.run("python3 -m venv venv")

    def clean_old_database_backups(self, nb_backups_to_keep):
        """
        Remove old database backups from the system and keep `nb_backups_to_keep`.
        """
        backups = self.ls(self.backups_root)
        backups = sorted(backups, reverse=True)

        if len(backups) > nb_backups_to_keep:
            backups_to_delete = backups[nb_backups_to_keep:]

            for backup_to_delete in backups_to_delete:
                self.run('rm "%s"' % os.path.join(self.backups_root, backup_to_delete))

            print("%d backups deleted." % len(backups_to_delete))
        else:
            print("No backups to delete.")

    def ls(self, path):
        """
        Return the list of the files in the given directory, omitting . and ...
        """
        with self.cd(path):
            files = self.run("for i in *; do echo $i; done").stdout.strip()
            files_list = files.replace("\r", "").split("\n")

        return files_list


def generate_secret_key():
    """
    Generate a random secret key, suitable to be used as a SECRET_KEY setting.
    """
    return "".join(
        [
            random.SystemRandom().choice(
                "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
            )
            for i in range(50)
        ]
    )


def is_supported_db_engine(engine):
    return engine == "django.db.backends.postgresql_psycopg2"


@task
@remote
def fetch_db(c, destination="."):
    """
    Dump the database on the remote host and retrieve it locally.

    The destination parameter controls where the dump should be stored locally.
    """
    dump_path = c.conn.dump_db("~")
    filename = os.path.basename(dump_path)

    subprocess.run(
        [
            "scp",
            "-P",
            str(c.conn.port),
            "{user}@{host}:{directory}".format(
                user=c.conn.user, host=c.conn.host, directory=dump_path
            ),
            destination,
        ]
    )
    c.conn.run("rm %s" % dump_path)

    return os.path.join(destination, filename)


@task
@remote
def import_db(c, dump_file=None):
    """
    Restore the given database dump.

    The dump must be a gzipped SQL dump. If the dump_file parameter is not set,
    the database will be dumped and retrieved from the remote host.
    """
    with open("envdir/DATABASE_URL", "r") as db_credentials_file:
        db_credentials = db_credentials_file.read()
    db_credentials_dict = dj_database_url.parse(db_credentials)

    if not is_supported_db_engine(db_credentials_dict["ENGINE"]):
        raise NotImplementedError(
            "The import_db task doesn't support your database engine"
        )

    if dump_file is None:
        dump_file = fetch_db(c)

    db_info = {
        "host": db_credentials_dict["HOST"],
        "user": db_credentials_dict["USER"],
        "db": db_credentials_dict["NAME"],
        "db_dump": dump_file,
    }

    c.run(
        "dropdb -h {host} -U {user} {db}".format(**db_info),
        env={"PGPASSWORD": db_credentials_dict["PASSWORD"].replace("$", "\$")},
    )
    c.run(
        "createdb -h {host} -U {user} {db}".format(**db_info),
        env={"PGPASSWORD": db_credentials_dict["PASSWORD"].replace("$", "\$")},
    )
    c.run(
        "gunzip -c {db_dump}|psql -h {host} -U {user} {db}".format(**db_info),
        env={"PGPASSWORD": db_credentials_dict["PASSWORD"].replace("$", "\$")},
    )


@task
@remote
def bootstrap(c):
    """
    Deploy the project for the first time. This will create the directory
    structure, push the project and set the basic settings.

    This task needs to be called alongside an environment task, eg. ``fab prod
    bootstrap``.
    """
    c.conn.create_structure()
    push_code_update(c, "HEAD")
    install_requirements(c)

    required_settings = set(
        [
            "DATABASE_URL",
            "MEDIA_ROOT",
            "STATIC_ROOT",
            "MEDIA_URL",
            "STATIC_URL",
            "ALLOWED_HOSTS",
        ]
    )

    env_settings = getattr(c.config, "settings", {})
    for setting, value in env_settings.items():
        c.conn.set_setting(setting, value=value)

    # Ask for settings that are required but were not set in the parameters
    # file
    for setting in required_settings - set(env_settings.keys()):
        c.conn.set_setting(setting)

    c.conn.set_setting(
        "DJANGO_SETTINGS_MODULE", value="%s.config.settings.base" % project_name
    )
    c.conn.set_setting("SECRET_KEY", value=generate_secret_key())

    compile_assets(c)
    dj_collect_static(c)
    dj_migrate_database(c)
    reload_uwsgi(c)


@task
@remote
def push_code_update(c, git_ref):
    """
    Synchronize the remote code repository
    """
    with c.conn.cd(c.conn.wwwroot):
        # First, check that the remote deployment directory exists
        try:
            c.conn.run("test -d .", hide=True)
        except UnexpectedExit:
            raise Exit(
                "Provisioning not finished, directory {} doesn't exist!".format(
                    c.config["root"]
                )
            )
        # Now make sure there's git, and a git repository
        try:
            c.conn.git("--version", hide=True)
        except UnexpectedExit:
            raise Exit("Provisioning not finished, git not available!")

        try:
            c.conn.git("rev-parse --git-dir", hide=True)
        except UnexpectedExit:
            c.conn.git("init")
            c.conn.git("checkout --orphan master")
            c.conn.put(StringIO("Bootstrap"), os.path.join(c.conn.wwwroot, "bootstrap"))
            c.conn.git("add bootstrap")
            c.conn.git('commit -m "First non-empty commit"')

    git_remote_url = "ssh://{user}@{host}:{port}/{directory}".format(
        user=c.conn.user, host=c.conn.host, port=c.conn.port, directory=c.conn.wwwroot
    )

    # Now push our code to the remote, always as FABHEAD branch
    porcelain.push(".", git_remote_url, "{}:FABHEAD".format(git_ref))

    with c.conn.cd(c.conn.wwwroot):
        c.conn.git("checkout -f master", hide=True)
        c.conn.git("reset --hard FABHEAD")
        c.conn.git("branch -d FABHEAD", hide=True)
        c.conn.git("submodule update --init", hide=True)


@task
@remote
def install_requirements(c):
    """
    Install project requirements in venv
    """
    try:
        # Test that pip works
        c.conn.pip("freeze", hide=True)
    except UnexpectedExit:
        c.conn.mk_venv()

    c.conn.pip("install -r requirements/base.txt")


@task
@remote
def sync_settings(c):
    """
    Synchronize the settings from the above environment to the server
    """
    for name, value in c.config.settings.items():
        c.conn.set_setting(name, value, force=True)


@task
@remote
def dj_collect_static(c):
    """
    Django: collect the statics
    """
    c.conn.manage_py("collectstatic --noinput")


@task
@remote
def dj_migrate_database(c):
    """
    Django: Migrate the database
    """
    c.conn.manage_py("migrate")


@task
@remote
def reload_uwsgi(c):
    """
    Django: Migrate the database
    """
    c.conn.run_in_wwwroot(
        "touch %s" % os.path.join(c.conn.wwwroot, project_name, "config", "wsgi.py")
    )


@task
def compile_assets(c):
    subprocess.run(["npm", "install"])
    subprocess.run(["npm", "run", "build"])

    subprocess.run(
        [
            "rsync",
            "-r",
            "-e",
            "ssh -p {port}".format(port=c.conn.port),
            "--exclude",
            "*.map",
            "--exclude",
            "*.swp",
            "static/dist/",
            "{user}@{host}:{path}".format(
                host=c.conn.host,
                user=c.conn.user,
                path=os.path.join(c.conn.project_root, "static"),
            ),
        ]
    )


@task
@remote
def deploy(c):
    """
    "Update" deployment
    """
    push_code_update(c, "HEAD")
    c.conn.dump_db(c.conn.backups_root)
    install_requirements(c)
    sync_settings(c)

    compile_assets(c)
    dj_collect_static(c)
    dj_migrate_database(c)
    reload_uwsgi(c)
    c.conn.clean_old_database_backups(nb_backups_to_keep=10)


# Environment handling stuff
############################
def create_environment_task(name, env_conf):
    """
    Create a task function from an environment name
    """

    @task(name=name)
    def load_environment(ctx):
        conf = env_conf.copy()
        conf["environment"] = name
        # So now conf is the ENVIRONMENTS[env] dict plus "environment" pointing to the name
        # Push them in the context config dict
        ctx.config.load_overrides(conf)
        # Add the common_settings in there
        ctx.conn = CustomConnection(host=conf["host"], inline_ssh_env=True)
        ctx.conn.config.load_overrides(conf)

    load_environment.__doc__ = (
        """Prepare connection and load config for %s environment""" % name
    )
    return load_environment


def load_environments_tasks(environments):
    """
    Load environments as fabric tasks
    """
    for name, env_conf in environments.items():
        globals()[name] = create_environment_task(name, env_conf)


# Yes, do it
load_environments_tasks(ENVIRONMENTS)
