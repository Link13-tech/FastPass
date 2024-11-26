# ���������� ����������� ����� Python
FROM python:3.12-slim

# ������������� ��������� �����������
RUN apt update && apt install -y gcc libpq-dev iputils-ping telnet postgresql-client

# ������������� Poetry
RUN pip install poetry

# ������������� ������� ����������
WORKDIR /app

# �������� ������ ����� ������������, ����� ���������� ��������� ������������
COPY pyproject.toml poetry.lock /app/

# ������������� ����������� � ������� Poetry (�� ��������� Poetry ������� ����������� ���������)
RUN poetry install --no-dev

# �������� ��������� ����� �������
COPY . /app/

# ��������� ���� ��� ����������
EXPOSE 8080

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]