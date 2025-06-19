alias g := generate
# Run cookiecutter with local template
generate:
  cookiecutter . -f --no-input

alias s := start
# Setup and start the playground project using Pontsun
start:
  cp my_project/docker-compose.override.example.yml my_project/docker-compose.override.yml
  sed -i '' -e '35,93 s/^# //' -e '35,93 s/^#//' my_project/docker-compose.override.yml
  cd my_project && docker-compose down
  cd my_project && INITIAL=1 docker-compose up --build --force-recreate
