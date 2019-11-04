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

SSH into the box and run:

```
npm start
```

Then point your browser to http://{{ cookiecutter.project_slug|replace('_', '-') }}.lo:3000/.
{% elif cookiecutter.virtualization_tool == 'docker' %}

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
