{{ cookiecutter.project_name }}
=======
{%- if cookiecutter.use_drifter == 'y' %}

Installation
------------

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

Front-end development
-------------

SSH into the box and run:

```
npm start
```

Then point your browser to http://{{ cookiecutter.project_slug|replace('_', '-') }}.lo:3000/.

{%- endif %}
