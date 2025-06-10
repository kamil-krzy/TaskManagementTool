FROM python:3.12-slim

# don't generate .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# disable output buffering (able to see logs in real-time)
ENV PYTHONUNBUFFERED=1

WORKDIR /TaskManagementTool

COPY ./tmt /TaskManagementTool/tmt
COPY ./tests /TaskManagementTool/tests
COPY pyproject.toml /TaskManagementTool/
COPY uv.lock /TaskManagementTool/


RUN pip install --upgrade pip && \
    pip install uv && \
    uv sync
