# 1. Imagem Base
# Usamos o Python slim para uma imagem final mais leve
FROM python:3.11-slim

# 2. Diretório de Trabalho
# Define o diretório onde sua aplicação estará dentro do container
WORKDIR /app

# 3. Instalação das Dependências
# Copia e instala todas as bibliotecas do seu requirements.txt
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar Código
# Copia o resto do seu projeto para o diretório de trabalho /app
# Certifique-se de que o 'run.py' e seus outros arquivos estejam aqui!
COPY . .

# 5. Porta
# Seu aplicativo provavelmente está configurado para rodar na porta 5000 (padrão Flask) 
# ou você definiu uma porta específica no seu run.py.
# É uma boa prática expor a porta que o app usa.
EXPOSE 5000

# 6. Comando de Início (CMD)
# **Este é o ponto chave:** Substituímos o Gunicorn pelo seu comando de inicialização!
# IMPORTANTE: Você precisa garantir que, dentro do seu 'run.py',
# o servidor Flask esteja configurado para escutar em '0.0.0.0' para que
# ele seja acessível fora do contêiner.

# O comando que o Docker irá executar para iniciar seu app:
CMD ["python", "run.py"]