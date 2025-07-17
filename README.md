# 📄 CV Maker Inteligente

Uma plataforma gratuita e inteligente para criação, análise e otimização de currículos com sugestões personalizadas baseadas em NLP (Processamento de Linguagem Natural).

## 🌟 Características Principais

- ✅ **Criação de CVs**: Interface intuitiva para criar e editar currículos
- 🤖 **Análise Inteligente**: Análise automática com NLP para melhorar o conteúdo
- 💡 **Sugestões Personalizadas**: Recomendações específicas por setor profissional
- 📊 **Sistema de Pontuação**: Score de 0-100 para qualidade do CV
- 📄 **Geração de PDF**: Download gratuito em formato profissional
- 🔐 **Autenticação Segura**: Sistema de login com JWT
- 📈 **Histórico e Estatísticas**: Acompanhe a evolução dos seus CVs
- 🔍 **Palavras-chave**: Identificação automática de termos relevantes

## 🛠️ Stack Tecnológica

### Backend
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para gestão da base de dados
- **SQLite**: Base de dados (facilmente migrável para PostgreSQL)
- **spaCy**: Processamento de linguagem natural
- **ReportLab**: Geração de PDFs
- **JWT**: Autenticação segura

### Frontend
- **Streamlit**: Interface web interativa e responsiva
- **Requests**: Comunicação com a API

### Análise NLP
- **spaCy**: Modelo português para análise de texto
- **Transformers**: Modelos de IA para análise avançada
- **scikit-learn**: Algoritmos de machine learning

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- pip (gestor de pacotes Python)

### 1. Clone o Repositório
```bash
git clone <repository-url>
cd CVmaker
```

### 2. Configuração Automática
```bash
python setup.py
```

Este script irá:
- Instalar todas as dependências
- Configurar modelos NLP
- Criar diretórios necessários
- Preparar o ambiente de desenvolvimento

### 3. Configuração Manual (Alternativa)

#### Instalar Dependências
```bash
pip install -r requirements.txt
```

#### Instalar Modelo NLP Português
```bash
python -m spacy download pt_core_news_sm
```

#### Criar Diretórios
```bash
mkdir -p storage/pdfs storage/logs database
```

## 🏃‍♂️ Como Executar

### 1. Iniciar o Backend (Terminal 1)
```bash
python run_backend.py
```
- API disponível em: http://localhost:8000
- Documentação: http://localhost:8000/docs

### 2. Iniciar o Frontend (Terminal 2)
```bash
python run_frontend.py
```
- Interface web: http://localhost:8501

### 3. Aceder à Aplicação
1. Abra o browser em http://localhost:8501
2. Crie uma conta ou faça login
3. Comece a criar os seus CVs!

## 📁 Estrutura do Projeto

```
CVmaker/
├── backend/                 # Backend FastAPI
│   └── app/
│       ├── api/            # Endpoints da API
│       ├── core/           # Configurações e segurança
│       ├── models/         # Modelos da base de dados
│       ├── services/       # Lógica de negócio
│       └── utils/          # Utilitários
├── frontend/               # Frontend Streamlit
│   └── streamlit/
├── config/                 # Configurações
├── storage/               # Armazenamento
│   ├── pdfs/             # PDFs gerados
│   └── logs/             # Logs do sistema
├── tests/                # Testes
├── docs/                 # Documentação
├── requirements.txt      # Dependências Python
├── setup.py             # Script de configuração
├── run_backend.py       # Executar backend
├── run_frontend.py      # Executar frontend
└── README.md           # Este arquivo
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente (.env)
```env
# Aplicação
APP_NAME=CV Maker Inteligente
DEBUG=True

# Base de Dados
DATABASE_URL=sqlite:///./cvmaker.db

# Segurança
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Armazenamento
PDF_STORAGE_PATH=./storage/pdfs
LOG_STORAGE_PATH=./storage/logs

# NLP
SPACY_MODEL=pt_core_news_sm
```

### Configuração para Produção
1. Altere `DEBUG=False` no .env
2. Configure uma chave secreta forte
3. Use PostgreSQL em vez de SQLite
4. Configure HTTPS
5. Use um servidor web como Nginx

## 📊 Funcionalidades Detalhadas

### Análise de CV
O sistema analisa automaticamente:
- **Verbos de Ação**: Identifica e sugere verbos impactantes
- **Resultados Quantificáveis**: Procura por números e métricas
- **Palavras-chave**: Extrai termos relevantes por setor
- **Estrutura**: Avalia organização e clareza
- **Comprimento**: Verifica se está no tamanho ideal

### Sugestões Personalizadas
- **Alta Prioridade**: Melhorias críticas (verbos de ação, resultados)
- **Média Prioridade**: Otimizações importantes (palavras-chave, estrutura)
- **Baixa Prioridade**: Ajustes menores (formatação, comprimento)

### Setores Suportados
- 💻 Tecnologia
- 📈 Marketing
- 💼 Vendas
- 👥 Recursos Humanos
- 💰 Finanças
- 🎯 Outros

## 🔍 API Endpoints

### Autenticação
- `POST /api/v1/auth/register` - Registar utilizador
- `POST /api/v1/auth/login` - Fazer login
- `GET /api/v1/auth/me` - Dados do utilizador

### CVs
- `POST /api/v1/cv/upload` - Criar CV
- `GET /api/v1/cv/` - Listar CVs do utilizador
- `GET /api/v1/cv/{id}` - Obter CV específico
- `POST /api/v1/cv/{id}/analyze` - Analisar CV
- `POST /api/v1/cv/{id}/generate-pdf` - Gerar PDF
- `GET /api/v1/cv/{id}/download-pdf` - Download PDF

### Utilizadores
- `GET /api/v1/users/profile` - Perfil do utilizador
- `GET /api/v1/users/stats` - Estatísticas
- `GET /api/v1/users/activity` - Histórico de atividade

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Testes com cobertura
pytest --cov=backend

# Testes específicos
pytest tests/test_cv_analyzer.py
```

## 📝 Logs

O sistema mantém logs detalhados:
- **Arquivo**: `storage/logs/cvmaker_YYYYMMDD.log`
- **Base de Dados**: Tabela `logs` com histórico completo
- **Níveis**: INFO, WARNING, ERROR

## 🚀 Roadmap Futuro

### Versão 2.0
- [ ] Templates visuais premium
- [ ] Geração automática de carta de apresentação
- [ ] Integração com LinkedIn
- [ ] Análise de compatibilidade com ofertas de emprego

### Versão 3.0
- [ ] Simulação de entrevista baseada no CV
- [ ] API pública para integrações
- [ ] Aplicação móvel
- [ ] Análise de mercado de trabalho

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para a sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit as suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

### Problemas Comuns

**Erro de modelo spaCy não encontrado:**
```bash
python -m spacy download pt_core_news_sm
```

**Erro de dependências:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Erro de permissões:**
```bash
# Linux/Mac
chmod +x run_backend.py run_frontend.py setup.py
```

### Contacto
- 📧 Email: suporte@cvmaker.com
- 🐛 Issues: GitHub Issues
- 💬 Discussões: GitHub Discussions

## 🙏 Agradecimentos

- spaCy pela excelente biblioteca de NLP
- FastAPI pela framework moderna e rápida
- Streamlit pela interface web simples e poderosa
- Comunidade Python pelo ecossistema incrível

---

**Desenvolvido com ❤️ para ajudar profissionais a criarem CVs de excelência!**
