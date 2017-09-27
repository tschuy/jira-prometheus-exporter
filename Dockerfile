FROM python:3.6.2-alpine3.6

MAINTAINER CoreOS Infrastructure Team <team-infra@coreos.com>
ADD . /src

RUN \
  python3.6 -m venv /venv && \
  source /venv/bin/activate && pip install -r /src/requirements.txt

ENV JIRAUSER="REPLACEME" \
    JIRAPASSWORD="REPLACEME"

# Installation complete!  Ensure that things can run properly:
ENTRYPOINT ["/venv/bin/python", "/src/main.py"]
