Django project template
==========================

To create a new project using this template, do the following (replace
`myproject` with the name of your project):

    pip install django
    django-admin.py startproject --template="https://github.com/liip/django-template/archive/master.zip" myproject

Once the project is created, you'll mostly want to add virtualization support
to be able to use the same setup on every computer. First, make sure you meet
all the
[requirements](https://github.com/team-rawbot/rawbot-virtualization#requirements)
then run the following commands.

    cd myproject
    git init .
    curl -sS https://raw.githubusercontent.com/team-rawbot/rawbot-virtualization/master/install.sh | /bin/bash

Start by editing the file `virtualization/parameters.yml` and uncomment the
following line:

    django_pip_requirements: "dev"

Also make sure to set the following settings to the value you want (again,
replace myproject with the name of your project):

    project_name: "myproject"
    database_name: "myproject"

Then edit the file `virtualization/playbook.yml` and uncomment the following
lines:

    - { role: postgresql }
    - { role: django }

Finally, run the following commands to get you project up and running:

    vagrant up
    vagrant ssh
    ./manage.py createsuperuser
    ./manage.py runserver

Go to http://django.lo/ and start hacking!

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
