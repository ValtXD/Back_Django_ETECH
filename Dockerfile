FROM python:3.12-slim

# Evita que o Python gere arquivos .pyc e mantém o buffer desabilitado
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copia o arquivo de dependências para o container
COPY requirements.txt /app/

# Instala dependências do sistema necessárias para o psycopg2, OpenCV e outras
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Atualiza pip, setuptools e wheel
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
# Copia o restante do código-fonte do projeto para o container
COPY . /app/

# Expondo a porta 8000 para acesso ao servidor Django
EXPOSE 8000

# Rodando o comando de migração e depois iniciando o servidor Django
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py migrate core --noinput && python manage.py runserver 0.0.0.0:8000"]