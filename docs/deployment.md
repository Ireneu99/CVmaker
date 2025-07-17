# 🚀 Guia de Deployment - CV Maker Inteligente

Este documento fornece instruções detalhadas para fazer o deployment da aplicação em diferentes ambientes.

## 🏠 Desenvolvimento Local

### Pré-requisitos
- Python 3.8+
- pip
- Git

### Setup Rápido
```bash
# 1. Clone o repositório
git clone <repository-url>
cd CVmaker

# 2. Execute o setup automático
python setup.py

# 3. Inicie o backend
python run_backend.py

# 4. Inicie o frontend (novo terminal)
python run_frontend.py
```

## ☁️ Deployment em Produção

### 1. Railway (Recomendado para Backend)

#### Preparação
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login
```

#### Deploy do Backend
```bash
# Criar projeto Railway
railway new

# Configurar variáveis de ambiente
railway variables set SECRET_KEY="your-super-secret-production-key"
railway variables set DATABASE_URL="postgresql://user:pass@host:port/db"
railway variables set DEBUG="False"
railway variables set ALLOWED_ORIGINS="https://your-frontend-domain.com"

# Deploy
railway up
```

#### Dockerfile para Railway
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy model
RUN python -m spacy download pt_core_news_sm

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Streamlit Cloud (Frontend)

#### Preparação
1. Faça push do código para GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte sua conta GitHub

#### Configuração
- **Repository**: seu-usuario/CVmaker
- **Branch**: main
- **Main file path**: frontend/streamlit/app.py

#### Secrets (Streamlit Cloud)
```toml
# .streamlit/secrets.toml
[general]
API_BASE_URL = "https://your-backend-url.railway.app/api/v1"
```

### 3. Render (Alternativa)

#### Backend no Render
```yaml
# render.yaml
services:
  - type: web
    name: cvmaker-backend
    env: python
    buildCommand: "pip install -r requirements.txt && python -m spacy download pt_core_news_sm"
    startCommand: "uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
```

### 4. Vercel (Frontend Alternativo)

#### Configuração
```json
{
  "builds": [
    {
      "src": "frontend/streamlit/app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "frontend/streamlit/app.py"
    }
  ]
}
```

## 🗄️ Base de Dados

### PostgreSQL (Produção)

#### Configuração
```bash
# Instalar dependências PostgreSQL
pip install psycopg2-binary

# Configurar DATABASE_URL
export DATABASE_URL="postgresql://username:password@host:port/database"
```

#### Migração de SQLite para PostgreSQL
```python
# Script de migração (migration.py)
import sqlite3
import psycopg2
from sqlalchemy import create_engine

def migrate_data():
    # Conectar às bases de dados
    sqlite_conn = sqlite3.connect('cvmaker.db')
    pg_engine = create_engine(os.getenv('DATABASE_URL'))
    
    # Migrar dados tabela por tabela
    # ... código de migração
```

### Supabase (Alternativa Gratuita)
```bash
# Configurar Supabase
pip install supabase

# DATABASE_URL
postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

## 🔒 Configuração de Segurança

### Variáveis de Ambiente (Produção)
```env
# Aplicação
APP_NAME=CV Maker Inteligente
DEBUG=False
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Base de Dados
DATABASE_URL=postgresql://user:pass@host:port/db

# Segurança
SECRET_KEY=your-super-secret-production-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Armazenamento
PDF_STORAGE_PATH=/app/storage/pdfs
LOG_STORAGE_PATH=/app/storage/logs

# NLP
SPACY_MODEL=pt_core_news_sm
```

### HTTPS e SSL
```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitorização

### Logs
```python
# Configurar logging para produção
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log', 
    maxBytes=10000000, 
    backupCount=5
)
logging.basicConfig(handlers=[handler])
```

### Health Checks
```python
# health_check.py
import requests
import time

def check_health():
    try:
        response = requests.get('https://your-api.com/health')
        return response.status_code == 200
    except:
        return False

# Executar a cada 5 minutos
while True:
    if not check_health():
        # Enviar alerta
        pass
    time.sleep(300)
```

## 🔄 CI/CD

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          python -m spacy download pt_core_news_sm
      - name: Run tests
        run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway login --token ${{ secrets.RAILWAY_TOKEN }}
          railway up
```

## 📱 Configuração de Domínio

### DNS
```
# Configuração DNS
A     @     your-server-ip
CNAME www   your-domain.com
```

### SSL Gratuito (Let's Encrypt)
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🚨 Backup e Recuperação

### Backup Automático
```bash
#!/bin/bash
# backup.sh

# Backup da base de dados
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup dos PDFs
tar -czf pdfs_backup_$(date +%Y%m%d_%H%M%S).tar.gz storage/pdfs/

# Upload para cloud storage
aws s3 cp backup_*.sql s3://your-backup-bucket/
aws s3 cp pdfs_backup_*.tar.gz s3://your-backup-bucket/
```

### Cron Job
```bash
# Adicionar ao crontab
0 2 * * * /path/to/backup.sh
```

## 📈 Escalabilidade

### Load Balancer
```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

### Redis Cache
```python
# Adicionar cache Redis
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_analysis(cv_text):
    cache_key = f"analysis:{hash(cv_text)}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    return None
```

## 🔍 Troubleshooting

### Problemas Comuns

**Erro de modelo spaCy:**
```bash
python -m spacy download pt_core_news_sm
```

**Erro de memória:**
```python
# Reduzir uso de memória
import gc
gc.collect()
```

**Timeout de requests:**
```python
# Aumentar timeout
requests.get(url, timeout=30)
```

### Logs de Debug
```python
# Ativar logs detalhados
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Suporte

Para problemas de deployment:
1. Verifique os logs da aplicação
2. Confirme as variáveis de ambiente
3. Teste a conectividade da base de dados
4. Verifique as permissões de ficheiros

---

**Boa sorte com o deployment! 🚀**
