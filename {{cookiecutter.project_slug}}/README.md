{{ cookiecutter.project_name }}
=======
{%- if cookiecutter.virtualization_tool == 'drifter' %}

## Installation

```
vagrant up
```

Then SSH into the box by running `vagrant ssh` and run:

```
npm install
npm run build
./manage.py runserver
```

Then point your browser to http://{{ cookiecutter.project_slug|replace('_', '-') }}.lo/.

## Front-end development

### Getting Started

SSH into the box and run:

```
npm start
```

Then point your browser to http://{{ cookiecutter.project_slug|replace('_', '-') }}.lo:3000/.
{% elif cookiecutter.virtualization_tool == 'docker' %}

### Build

You can build a static version of your assets inside the box:

```bash
npm run build
```

### Formatting and Linting

It’s recommended to have Prettier, EsLint and Stylelint enabled in your Editor.

You can manually check that the code matches with the guidelines by running:

```bash
npm run validate
```

You can automatically fix all the offenses tools are capable of by running:

```bash
npm run format
```

## Dev setup

1. Open the file `docker-compose.override.example.yml` and follow the instructions in it

2. Run the command `INITIAL=1 docker-compose up`

This will start the containers and set up the initial data. To access the site,
follow the instructions in the `docker-compose.override.example.yml` file.

Note the `INITIAL` flag should not be set for subsequent container starts unless
you want to reset the database.

## Automated tests

To run backend tests and lint checks, run `scripts/run_tests.sh` in the `backend` container:
* `docker-compose exec backend scripts/run_tests.sh`
* or `docker-compose run --rm backend scripts/run_tests.sh` if the `backend` service is not already running

CLI arguments are forwarded to `pytest`.
For example, running tests with `scripts/run_tests.sh {{ cookiecutter.project_slug }} --reuse-db` avoids
re-creating the database from scratch on each run.

{%- endif %}

## Deploying


Before deploying, you should update the CHANGELOG.md file with the latest changes by running:
 ```
 docker-compose exec backend fab <environment> generate-changelog
```

**Note**: this step is not strictly required, but be aware that the CHANGELOG.md file should reflect the current status
of the project. For example, you might not want to update the changelog if you are pushing an urgent hotfix/doing tests.


To deploy the site, run:
 ```
 docker-compose exec backend fab <environment> deploy
```

Where _<environment>_ can either be _prod_ or _staging_. To see all the available Fabric commands, run:

```
 docker-compose exec backend fab -l
```

If the deployment command asks you for a password, make sure you have _ssh-agent_ running on your host and your SSH key
has been added to it (using `ssh-add`) and that it has been forwarded to the box when you SSHed into it.

Make sure `fab <environment> bootstrap` has already been run before the first ever deployment.
