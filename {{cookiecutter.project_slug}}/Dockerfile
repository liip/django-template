FROM python:3.11-bookworm

RUN set -x; \
    export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -qq \
    && apt-get install -yq \
        gettext \
        # Needed to build and deploy frontend assets from fabfile
        rsync \
        # Not required. Only for development QoL.
        bash-completion postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ENV NODE_VERSION="20.18.0"
ENV NVM_DIR="/opt/nvm"
RUN mkdir "$NVM_DIR" \
    && curl https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION

ENV NODE_PATH="$NVM_DIR/versions/node/v$NODE_VERSION/lib/node_modules"
ENV PATH="$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH"

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
RUN set -x; \
    python -m venv "$VIRTUAL_ENV" && \
    "$VIRTUAL_ENV/bin/pip" install wheel && \
    "$VIRTUAL_ENV/bin/pip" install pip-tools
WORKDIR /code

COPY entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]
