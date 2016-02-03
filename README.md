Django project template
==========================

To create a new project using this template, do the following:

    pip install cookiecutter pip-tools
    cookiecutter gh:liip/django-template

Then run the following commands to get your project up and running:

    vagrant up
    vagrant ssh
    ./manage.py createsuperuser
    ./manage.py runserver

Go to http://my-project.lo/ and start hacking!

Deploying your site
-------------------

You can use the provided `fabfile` to deploy your site. Before using it, check
the `fabfile.py` file and adjust the settings at the top of the file. You'll
also need to install the following Python packages that are required by the
deployment process:

    pip install -r requirements/deploy.txt

Once the settings are adjusted and the dependencies installed, you can use the
`bootstrap` command that will create the directory structure, push the code to
the server and deploy your project. For example, the following command will
bootstrap your dev environment:

    fab dev bootstrap

You'll have to run the bootstrap command for each of the environments you want
to bootstrap. After the site is bootstrapped, subsequent deployments can be
done with the `deploy` command. The `deploy` command takes one required
argument, which is the revision to deploy. This can be any valid git hash, eg.
a tag, a branch name or even a commit hash. For example to deploy the current
master branch on the dev environment, use the following:

    fab dev deploy:master
