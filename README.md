# Django project template

To create a new project using this template, do the following:

    pip install cookiecutter
    cookiecutter gh:liip/django-template

Go to http://my-project.docker.test/ and start hacking!

## Troubleshooting

If you get the following error when running `cookiecutter`:

```
Traceback (most recent call last):
  File "/home/me/.virtualenvs/tmp-1081dbf5557421f7/bin/pip-compile", line 7, in <module>
    from piptools.scripts.compile import cli
  File "/home/me/.virtualenvs/tmp-1081dbf5557421f7/local/lib/python2.7/site-packages/piptools/scripts/compile.py", line 16, in <module>
    from ..repositories import PyPIRepository
  File "/home/me/.virtualenvs/tmp-1081dbf5557421f7/local/lib/python2.7/site-packages/piptools/repositories/__init__.py", line 2, in <module>
    from .pypi import PyPIRepository
  File "/home/me/.virtualenvs/tmp-1081dbf5557421f7/local/lib/python2.7/site-packages/piptools/repositories/pypi.py", line 10, in <module>
    from pip.req.req_set import RequirementSet
ImportError: No module named req_set
```

That's because your `pip` version is too old. Upgrade it either with your
package manager, or by running `pip install --upgrade pip`.

## Deploying your site

You can use the provided `fabfile` to deploy your site. Before using it, check
the `fabfile.py` file and adjust the settings at the top of the file.

Once the settings are adjusted and the dependencies installed, you can use the
`bootstrap` command that will create the directory structure, push the code to
the server and deploy your project. For example, the following command will
bootstrap your dev environment:

    fab dev bootstrap

You'll have to run the bootstrap command for each of the environments you want
to bootstrap. After the site is bootstrapped, subsequent deployments can be
done with the `deploy` command:

    fab dev deploy

## Contributing

If you don’t happen to have [just](https://github.com/casey/just) installed, take a look at the `justfile` and run the commands manually.

You can easily generate a new project using this template by running:

```bash
just generate
```

After that, quickly configure and start Docker with Pontsun by running:

```bash
just start
```
