# AGENTS.md

## What this repository is

This is a **cookiecutter** template that scaffolds a Django project. There is
no application here to run directly — the source of truth is the Jinja-rendered
template under `{{cookiecutter.project_slug}}/`. Edits to that tree only take
effect after a project is generated from the template.

## Repository layout

- `cookiecutter.json` — template variables (project name/slug, language list,
  `virtualization_tool` (`docker` or `nothing`), `override_user_model`).
- `hooks/post_gen_project.py` — runs after generation: removes Docker files
  when `virtualization_tool != docker`, drops the `accounts` app when
  `override_user_model == n`, and creates blank locale `.po` files for each
  language in `language_list`.
- `{{cookiecutter.project_slug}}/` — the template body (rendered output root).
- `justfile` (repo root) — shortcuts to generate the template and run the
  resulting project locally with Pontsun.

## What the generated project (`{{cookiecutter.project_slug}}`) contains

After rendering, the directory becomes the project slug (e.g. `my_project/`).
Anything inside `{{cookiecutter.project_slug}}/` that uses `{{ cookiecutter.* }}`
markers is templated by Jinja; `*.html` files are excluded from rendering
(see `_copy_without_render` in `cookiecutter.json`). Strings that need to keep
double-braces in the output (Django/Jinja syntax inside `justfile`) are escaped
with `{{ '{{' }}`.

The generated project is a Django app served via Docker Compose with:

- **`backend`** — Python 3.11 + Django, Vite integration through `django_vite`,
  `debug_toolbar` and `django_extensions` in dev. Settings split into
  `config/settings/{base,dev,test}.py`; env-driven via `dj_database_url` and
  `dj_email_url`. `runserver` is the default command (auto-restart loop in
  `docker-compose.yml`).
- **`frontend`** — Node 20 + Vite (port 3000), Tailwind v4, ESLint + Prettier.
- **`db`** — Postgres 15.
- **`mailpit`** — fake SMTP/UI for outgoing mail (`EMAIL_URL` points at it).

Apps inside the project package:
- `core` — base app, holds the `fixturize` management command.
- `accounts` — only when `override_user_model == y`; provides a custom
  `User(AbstractUser)` wired via `AUTH_USER_MODEL = "accounts.User"`.

Per-project tooling:
- `justfile` — wraps everything in `docker compose exec`: `start`, `bash`,
  `manage`/`dj`, `shell_plus`, `test`, `lint`, `format`, `compile`,
  `compile-upgrade`, `install`, `makemigrations`, `migrate`, `fixturize`,
  `translate`, `npm`. Aliases like `t`, `l`, `fix`, `mm`, `m`, `f` exist.
- `scripts/run_tests.sh` — used by CI; runs `check_migrations.sh` (dry-run
  `makemigrations` against sqlite), then `pytest`, then `ruff check`.
- `pyproject.toml` — ruff config (`select = ["F", "I", "T10"]`, line length 88).
- `setup.cfg` — pytest config: `DJANGO_SETTINGS_MODULE = …config.settings.test`,
  coverage enabled on the project package.

## How to test changes to the template

The template itself has no test suite — verify changes by generating a project
and exercising it.

1. **Regenerate the playground project** (from the repo root):

   ```bash
   just generate    # alias: just g
   ```

   This wipes `node_modules` and any previous `my_project/`, then runs
   `cookiecutter . --no-input` using the defaults from `cookiecutter.json`
   (project name `My Project` → slug `my_project`, docker, accounts on).

2. **Boot the generated project**:

   ```bash
   just start       # alias: just s
   ```

   This copies `docker-compose.override.example.yml` to `…override.yml`,
   uncomments the Pontsun block, brings the stack down, then runs
   `INITIAL=1 docker-compose up --build --force-recreate`. With Pontsun set up
   the site is reachable at `https://my-project.docker.test/` and Mailpit at
   `https://my-project-mail.docker.test/`. Without Pontsun, edit the override
   to use the minimal port-mapping block (8000/3000/8025 on localhost).

   Note: `just start` uses BSD `sed -i ''` syntax — on GNU sed (Linux) the
   first `sed` call will fail. If you're on Linux, either uncomment the
   override block manually or adjust the `sed` invocation.

3. **Exercise the generated project** from inside `my_project/`:

   ```bash
   cd my_project
   just test                       # pytest in backend container
   just lint                       # ruff + npm run validate
   just manage check               # Django system check
   just manage makemigrations --dry-run --check
   just fixturize                  # reset DB + load fixtures
   ```

   For backend-only iteration without docker-compose orchestration:
   `docker-compose run --rm backend scripts/run_tests.sh` mirrors CI.

4. **Smoke-test in a browser** when changes touch templates, settings, Vite,
   or static assets. Visit the site, check Django Debug Toolbar appears in
   dev, confirm Vite HMR works, and send a test email to confirm Mailpit
   captures it.

5. **Cover the matrix** when changes touch templated logic. Cookiecutter
   variables that meaningfully change output:
   - `virtualization_tool = nothing` — exercises `uninstall_docker()` in the
     post-gen hook (removes Dockerfiles, `docker-compose.*`, `.gitlab-ci.yml`).
   - `override_user_model = n` — removes the `accounts` app and the
     `AUTH_USER_MODEL` setting.
   - Changing `language_list` / `default_language` — the post-gen hook
     creates one empty `locale/<lang>/LC_MESSAGES/django.po` per entry, and
     `base.py` renders the `LANGUAGES` tuple.

   Re-run `cookiecutter . --no-input --config-file <override>` or pass
   `-f` with explicit `--extra-context` to generate variants.

## Things to keep in mind when editing the template

- Anything under `{{cookiecutter.project_slug}}/` is rendered by Jinja. Literal
  `{{` and `}}` that must survive into the generated file (e.g. Django
  templates, justfile `{{ '{{' }} VAR }}`) need escaping.
- HTML files are copied verbatim (see `_copy_without_render`); use template
  tags rather than cookiecutter variables inside them.
- The post-gen hook runs in the **rendered** directory — paths inside it are
  relative to the generated project root, and the hook itself is rendered, so
  `{{ cookiecutter.* }}` is available there too.
- The repo-root `justfile` only covers generation; the per-project `justfile`
  (templated) is what end users see. Keep parity between the two when adding
  helpers that should be exposed downstream.
