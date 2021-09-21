import functools
import inspect
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

    call_task_with_connection.__signature__ = inspect.signature(task_func)
    return call_task_with_connection


def ensure_absolute_path(path):
    if not os.path.isabs(path):
        raise ValueError("{!r} is not an absolute path.".format(path))


class CustomConnection(Connection):
    """
    Add helpers function on Connection
    """

    @property
    def site_root(self):
        return self.config.root

    @property
    def project_root(self):
        """
        Return the path to the root of the project on the remote server.
        """
        return os.path.join(self.site_root, project_name)

    @property
    def venv_path(self):
        return os.path.join(self.site_root, "venv")

    @property
    def envdir_path(self):
        return os.path.join(self.project_root, "envdir")

    @property
    def backups_root(self):
        """
        Return the path to the backups directory on the remote server.
        """
        return os.path.join(self.site_root, "backups")

    @property
    def media_root(self):
        """
        Return the path to the media directory on the remote server.
        """
        try:
            path = self.config.settings["MEDIA_ROOT"]
        except KeyError:
            return os.path.join(self.site_root, "media")
        else:
            ensure_absolute_path(path)
            return path

    @property
    def static_root(self):
        """
        Return the path to the static directory on the remote server.
        """
        try:
            path = self.config.settings["STATIC_ROOT"]
        except KeyError:
            return os.path.join(self.site_root, "static")
        else:
            ensure_absolute_path(path)
            return path

    def run_in_project_root(self, cmd, **kwargs):
        """
        Run command after a cd to the project_root
        """
        with self.cd(self.project_root):
            return self.run(cmd, **kwargs)

    def git(self, gitcmd, **kwargs):
        """
        git from the project_root
        """
        return self.run_in_project_root("git {}".format(gitcmd), **kwargs)

    def run_in_venv(self, cmd, args, **run_kwargs):
        """
        Binaries from the venv
        """
        return self.run_in_project_root(
            "{} {}".format(os.path.join(self.venv_path, "bin", cmd), args), **run_kwargs
        )

    def mk_venv(self, **run_kwargs):
        """
        Create the venv
        """

        with self.cd(self.site_root):
            self.run("python3 -m venv venv", **run_kwargs)

    def pip(self, args, **run_kwargs):
        """
        pip from the venv, in the project_root
        """
        return self.run_in_venv("pip", args, **run_kwargs)

    def python(self, args, **run_kwargs):
        """
        python from the venv, in the project_root
        """
        return self.run_in_venv("python", args, **run_kwargs)

    def manage_py(self, args, **run_kwargs):
        """
        manage.py with the python from the venv, in the project_root
        """
        try:
            env = {
                "DJANGO_SETTINGS_MODULE": self.config.settings["DJANGO_SETTINGS_MODULE"]
            }
        except KeyError:
            env = {}
        return self.python("./manage.py {}".format(args), env=env, **run_kwargs)

    def set_setting(self, name, value=None, force: bool = True):
        """
        Set a setting in the environment directory, for use by Django
        """
        envfile_path = os.path.join(self.envdir_path, name)

        will_write = force
        if not force:
            try:
                # Test that it does exist
                self.run_in_project_root("test -r {}".format(envfile_path), hide=True)
            except UnexpectedExit:
                will_write = True

        if will_write:
            if value is None:
                value = input("Value for {}: ".format(name))

            # Convert booleans into values understood as such by Django
            if isinstance(value, bool):
                value = "1" if value else ""
            self.put(StringIO("{}\n".format(value)), envfile_path)

    def dump_db(self, destination):
        """
        Dump the database to the given directory and return the path to the file created.
        This creates a gzipped SQL file.
        """
        with self.cd(self.project_root):
            env_file = os.path.join(self.envdir_path, "DATABASE_URL")
            db_credentials = self.run("cat " + env_file, hide=True).stdout.strip()

        db_credentials_dict = dj_database_url.parse(db_credentials)

        if not is_supported_db_engine(db_credentials_dict["ENGINE"]):
            raise NotImplementedError(
                "The dump_db task doesn't support the remote database engine"
            )

        outfile = os.path.join(
            destination, datetime.now().strftime("%Y-%m-%d_%H%M%S.sql.gz")
        )

        self.run(
            "pg_dump -O -x -h '{host}' -U '{user}' '{db}'|gzip > {outfile}".format(
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
        command = " ".join(
            [
                "mkdir -p",
                self.project_root,
                self.backups_root,
                self.static_root,
                self.media_root,
            ]
        )
        self.run(command)

    def clean_old_database_backups(self, nb_backups_to_keep):
        """
        Remove old database backups from the system and keep `nb_backups_to_keep`.
        """
        backups = self.ls(self.backups_root)
        backups = sorted(backups, reverse=True)

        if len(backups) > nb_backups_to_keep:
            backups_to_delete = backups[nb_backups_to_keep:]
            file_to_remove = [
                os.path.join(self.backups_root, backup_to_delete)
                for backup_to_delete in backups_to_delete
            ]
            self.run('rm "%s"' % '" "'.join(file_to_remove))
            print("%d backups deleted." % len(backups_to_delete))
        else:
            print("No backups to delete.")

    def ls(self, path):
        """
        Return the list of the files in the given directory, omitting . and ...
        """
        with self.cd(path):
            files = self.run("for i in *; do echo $i; done", hide=True).stdout.strip()
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
    return engine in [
        "django.db.backends.postgresql_psycopg2",
        "django.db.backends.postgresql",
        "django.contrib.gis.db.backends.postgis",
    ]


def print_commits(commits):
    for rev, message in commits:
        print(f"{rev} {message}")


def get_outgoing_commits(c):

    with c.conn.cd(c.conn.project_root):
        remote_tip = c.conn.git("rev-parse HEAD", hide=True, pty=False).stdout.strip()
        commits = subprocess.run(f"git log --no-color --oneline {remote_tip}..".split(" "), text=True, capture_output=True).stdout.strip()
        outgoing = to_commits_list(commits)

    return outgoing


@task
@remote
def outgoing_commits(c):
    print("The following commits are not on the remote branch:\n")
    print_commits(get_outgoing_commits(c))


def get_local_modifications_count():
    return len(
        [
            line
            for line in subprocess.run("git status -s".split(" "), text=True, capture_output=True).stdout.splitlines()
            if line.strip()
        ]
    )


@task
@remote
def log(c):
    with c.conn.cd(c.conn.project_root):
        commits = c.conn.git("log --no-color --oneline -n 20", hide=True, pty=False).stdout.strip()

    print_commits(to_commits_list(commits))


def to_commits_list(log_str):
    return [tuple(log_line.split(maxsplit=1)) for log_line in log_str.splitlines()]


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
def import_db(c, dump_file=None):
    """
    Restore the given database dump.

    The dump must be a gzipped SQL dump. If the dump_file parameter is not set,
    the database will be dumped and retrieved from the remote host.
    """
    db_credentials = os.environ.get("DATABASE_URL")
    if not db_credentials:
        with open("envdir/DATABASE_URL", "r") as db_credentials_file:
            db_credentials = db_credentials_file.read()
    db_credentials_dict = dj_database_url.parse(db_credentials)

    if not is_supported_db_engine(db_credentials_dict["ENGINE"]):
        raise NotImplementedError(
            "The import_db task doesn't support your database engine"
        )

    if dump_file is None:
        dump_file = fetch_db(c)

    pg_opts_mapping = {
        "-h": db_credentials_dict["HOST"],
        "-U": db_credentials_dict["USER"],
    }
    pg_opts = " ".join(
        [f"{option} '{value}'" for option, value in pg_opts_mapping.items() if value]
    )
    db_name = db_credentials_dict["NAME"]
    db_info = {"pg_opts": pg_opts, "db": db_name}

    env = {"PGPASSWORD": db_credentials_dict["PASSWORD"].replace("$", "\\$")}
    close_sessions_command = """
        psql {pg_opts} template1 -c "
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db}' AND pid != pg_backend_pid();
        "
    """.strip()
    c.run(close_sessions_command.format(**db_info), env=env, hide="out")
    c.run("dropdb {pg_opts} '{db}'".format(**db_info), env=env)
    c.run("createdb {pg_opts} '{db}'".format(**db_info), env=env)
    c.run(
        "gunzip -c {db_dump}|psql {pg_opts} '{db}'".format(
            db_dump=dump_file, **db_info
        ),
        env=env,
        hide="out",
    )


@task
@remote
def deploy(c, noconfirm='n'):
    """
    Execute all deployment steps
    """

    # Prerequisite steps
    noconfirmed = noconfirm.lower() in ("y", "yes")
    outgoing_commits(c)
    if not noconfirmed and input(
        "Do you want to proceed with the deployment of the above commits ? [y/N] "
    ).lower() not in ("y", "yes"):
        return

    local_modification_count = get_local_modifications_count()
    if not noconfirmed and local_modification_count > 0:
        if input(
            f"Warning ! There are {local_modification_count} local files that are not commited. "
            f"Do you want to proceed ? [y/N] "
        ).lower() not in ("y", "yes"):
            return

    compile_assets()
    c.conn.create_structure()
    push_code_update(c, "HEAD")
    sync_settings(c)
    c.conn.dump_db(c.conn.backups_root)
    install_requirements(c)
    sync_assets(c)
    dj_collect_static(c)
    dj_migrate_database(c)
    reload_uwsgi(c)
    c.conn.clean_old_database_backups(nb_backups_to_keep=10)


@task
@remote
def push_code_update(c, git_ref):
    """
    Synchronize the remote code repository
    """
    with c.conn.cd(c.conn.project_root):
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

    git_remote_url = "ssh://{user}@{host}:{port}/{directory}".format(
        user=c.conn.user,
        host=c.conn.host,
        port=c.conn.port,
        directory=c.conn.project_root,
    )

    # Now push our code to the remote, always as FABHEAD branch
    porcelain.push(".", git_remote_url, "{}:FABHEAD".format(git_ref))

    with c.conn.cd(c.conn.project_root):
        c.conn.git("checkout -f -B master FABHEAD", hide=True)
        c.conn.git("branch -d FABHEAD", hide=True)
        c.conn.git("submodule update --init", hide=True)


@task
@remote
def install_requirements(c):
    """
    Install project requirements in venv
    """
    try:
        c.conn.run("test -r {}".format(c.conn.venv_path), hide=True)
    except UnexpectedExit:
        c.conn.mk_venv()

    c.conn.pip("install -r requirements/base.txt")


@task
@remote
def sync_settings(c):
    """
    Synchronize the settings from the above environment to the server
    """

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
        c.conn.set_setting(setting, force=False)

    c.conn.set_setting(
        "DJANGO_SETTINGS_MODULE",
        value="%s.config.settings.base" % project_name,
        force=False,
    )
    c.conn.set_setting("SECRET_KEY", value=generate_secret_key(), force=False)


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
    Reload uWSGI workers
    """
    c.conn.run_in_project_root(
        "touch %s"
        % os.path.join(c.conn.project_root, project_name, "config", "wsgi.py")
    )


def compile_assets():
    subprocess.run(["npm", "install"])
    subprocess.run(["npm", "run", "build"])


@task
@remote
def sync_assets(c):
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
            "static/dist",
            "{user}@{host}:{path}".format(
                host=c.conn.host,
                user=c.conn.user,
                path=os.path.join(c.conn.project_root, 'static'),
            ),
        ]
    )


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
