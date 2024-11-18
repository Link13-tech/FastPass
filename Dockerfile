# ���������� ����������� ����� Python
FROM python:3.12-slim

# ������������� ��������� �����������
RUN apt update && apt install -y gcc libpq-dev

# ������������� Poetry
RUN pip install poetry

# ������������� ������� ����������
WORKDIR /app

# �������� ������ ����� ������������, ����� ���������� ��������� ������������
COPY pyproject.toml poetry.lock /app/

# ������������� ����������� � ������� Poetry (�� ��������� Poetry ������� ����������� ���������)
RUN poetry install --no-dev

# ��������, ��� alembic ��������
RUN poetry run alembic --version

# �������� ��������� ����� �������
COPY . /app/


# ������� ���������� ��� ����� (���� ������������ ����������� � �����)
RUN mkdir -p /app/logs && chmod -R 755 /app/logs

# ��������� ���� ��� ����������
EXPOSE 8080

# ������� ��� ������� ����������
CMD ["bash", "-c", "poetry run alembic upgrade head && poetry run uvicorn main:app --host 0.0.0.0 --port 8080"]