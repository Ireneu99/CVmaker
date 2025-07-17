# 🎯 Guia de Demonstração - CV Maker Inteligente

## 🚀 Como Usar a Aplicação

### 1. **Acesso à Aplicação**
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs

### 2. **Registo de Novo Utilizador**
1. Aceda a http://localhost:8501
2. Clique no separador "Registar"
3. Preencha os campos:
   - **Nome de utilizador**: alexandre99
   - **Email**: alexandre99@email.com
   - **Nome completo**: Alexandre Silva
   - **Palavra-passe**: Alexandre99@
   - **Confirmar palavra-passe**: Alexandre99@
4. Clique em "Registar"

### 3. **Login**
1. Após o registo, vá ao separador "Login"
2. Introduza as credenciais:
   - **Nome de utilizador**: alexandre99
   - **Palavra-passe**: Alexandre99@
3. Clique em "Entrar"

### 4. **Criar um CV**
1. No dashboard, clique em "Criar CV"
2. Preencha:
   - **Título**: "Meu CV Profissional"
   - **Setor**: Selecione "tecnologia"
   - **Conteúdo**: Cole o exemplo abaixo

```
Nome: Alexandre Silva
Email: alexandre99@email.com
Telefone: +351 912 345 678

Objetivo:
Desenvolvedor Python com 3 anos de experiência em desenvolvimento web e APIs.

Experiência Profissional:
- Desenvolvedor Backend na TechCorp (2021-2024)
  - Desenvolvi APIs REST usando FastAPI
  - Implementei sistemas de autenticação JWT
  - Melhorei performance das consultas em 40%
  - Trabalhei com PostgreSQL e Redis

- Estagiário de Desenvolvimento na StartupXYZ (2020-2021)
  - Criei scripts de automação em Python
  - Ajudei na migração de dados
  - Aprendi metodologias ágeis

Educação:
- Licenciatura em Engenharia Informática - Universidade do Porto (2020)
- Curso de Python Avançado - Udemy (2021)

Competências Técnicas:
- Python, FastAPI, Django
- JavaScript, React, Node.js
- PostgreSQL, MongoDB, Redis
- Docker, Git, AWS
- HTML, CSS, Bootstrap

Competências Pessoais:
- Trabalho em equipa
- Resolução de problemas
- Comunicação eficaz
- Aprendizagem contínua

Projetos:
- Sistema de Gestão de Inventário (Python/FastAPI)
- Website de E-commerce (React/Node.js)
- API de Análise de Dados (Python/Pandas)

Idiomas:
- Português (Nativo)
- Inglês (Fluente)
- Espanhol (Intermédio)
```

3. Clique em "Criar CV"

### 5. **Análise Automática**
- O sistema irá analisar automaticamente o CV
- Verá uma pontuação de 0-100
- Receberá sugestões personalizadas de melhoria
- Palavras-chave relevantes serão identificadas

### 6. **Gerar PDF**
1. Vá a "Meus CVs"
2. Encontre o CV criado
3. Clique em "Gerar PDF"
4. Depois clique em "Download PDF"

### 7. **Explorar Funcionalidades**
- **Dashboard**: Veja estatísticas pessoais
- **Meus CVs**: Gerir todos os CVs criados
- **Estatísticas**: Análise detalhada da atividade
- **Atividade**: Histórico completo de ações

## 🎯 Funcionalidades de IA Demonstradas

### **Análise Inteligente**
- Deteta falta de verbos de ação
- Identifica ausência de resultados quantificados
- Sugere melhorias na estrutura
- Analisa adequação ao setor escolhido

### **Sugestões Personalizadas**
- **Alta Prioridade**: Problemas críticos
- **Média Prioridade**: Melhorias importantes
- **Baixa Prioridade**: Otimizações menores

### **Exemplos de Sugestões**
- "Use verbos de ação no início das frases"
- "Adicione resultados quantificados (%, números)"
- "Inclua mais palavras-chave do setor tecnologia"
- "Melhore a estrutura das secções"

## 🔧 Testes da API

### **Endpoints Principais**
```bash
# Registo
POST http://localhost:8000/api/v1/auth/register

# Login
POST http://localhost:8000/api/v1/auth/login

# Upload CV
POST http://localhost:8000/api/v1/cv/upload

# Análise CV
POST http://localhost:8000/api/v1/cv/{cv_id}/analyze

# Gerar PDF
POST http://localhost:8000/api/v1/cv/{cv_id}/generate-pdf
```

## 📊 Logs e Monitorização

### **Logs de Sistema**
- Todos os logs são guardados em `storage/logs/`
- Logs de API requests com tempo de execução
- Logs de erros com stack traces
- Logs de atividade do utilizador

### **Base de Dados**
- SQLite: `cvmaker.db`
- Tabelas: users, cvs, logs
- Dados persistentes entre sessões

## 🎉 Demonstração Completa

Esta aplicação demonstra:
1. **Autenticação segura** com JWT
2. **Análise de CV com NLP** usando spaCy
3. **Sugestões inteligentes** personalizadas
4. **Geração de PDF** profissional
5. **Interface web moderna** com Streamlit
6. **API REST completa** com FastAPI
7. **Sistema de logs** robusto
8. **Arquitetura escalável** e modular

O projeto está pronto para produção e pode ser facilmente expandido com novas funcionalidades de IA.
