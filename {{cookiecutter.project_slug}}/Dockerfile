FROM python:3.9-bullseye

# Needed to build assets in the deployment process
RUN set -x; \
    export DEBIAN_FRONTEND=noninteractive \
    && echo "deb https://deb.nodesource.com/node_16.x bullseye main" > /etc/apt/sources.list.d/nodesource.list \
    && curl -sSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - \
    && apt-get update -qq \
    && apt-get install -yq \
        gettext \
        # Needed to build and deploy frontend assets from fabfile
        nodejs rsync \
        # Not required. Only for development QoL.
        bash-completion postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ARG USER_ID=1000
ARG GROUP_ID=1000

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV VIRTUAL_ENV="/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN set -x; \
    groupadd -g $GROUP_ID app && \
    useradd --create-home -u $USER_ID -g app -s /bin/bash app && \
    install -o app -g app -d /code "$VIRTUAL_ENV"

RUN mkdir /opt/media
RUN chown -R $USER_ID:$USER_ID /opt/media

USER app
RUN python -m venv "$VIRTUAL_ENV" && "$VIRTUAL_ENV/bin/pip" install wheel
WORKDIR /code

COPY entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]
