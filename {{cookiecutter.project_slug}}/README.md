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

## Maintaining translations

1. `make translations  # Regenerate .po files`
2. Visit http://localhost:8000/rosetta/ and start translating!

It's safe to run this locally, even if you use Docker. (The Docker image is missing the GNU gettext tools and the command will not work anyway.)
