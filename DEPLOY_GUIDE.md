# 🚀 Guia de Deploy Gratuito - CV Maker Inteligente

## 📋 Opções de Deploy Gratuito

### 1. 🌟 **Streamlit Cloud (RECOMENDADO)**
**✅ Completamente gratuito e fácil**

#### Passos:
1. **Push para GitHub**:
   ```bash
   git add .
   git commit -m "Deploy ready"
   git push origin main
   ```

2. **Aceder ao Streamlit Cloud**:
   - Ir para [share.streamlit.io](https://share.streamlit.io)
   - Fazer login com GitHub
   - Clicar em "New app"

3. **Configurar Deploy**:
   - **Repository**: `Ireneu99/CVmaker`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
   - **Python version**: 3.9

4. **Deploy**:
   - Clicar "Deploy!"
   - Aguardar 2-3 minutos
   - **Link público será gerado automaticamente!**

#### 🔗 **Link de Exemplo**: `https://cvmaker-inteligente.streamlit.app`

---

### 2. 🐙 **GitHub Codespaces (Alternativa)**
**✅ Gratuito com conta GitHub**

#### Passos:
1. No repositório GitHub, clicar em "Code" > "Codespaces"
2. Criar novo Codespace
3. Executar:
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```
4. Partilhar o link público gerado

---

### 3. 🌐 **Replit (Alternativa)**
**✅ Gratuito e simples**

#### Passos:
1. Ir para [replit.com](https://replit.com)
2. Importar do GitHub: `https://github.com/Ireneu99/CVmaker`
3. Configurar como Python
4. Executar: `streamlit run streamlit_app.py`
5. Link público gerado automaticamente

---

## 🔧 **Configuração Rápida**

### Ficheiros Criados para Deploy:
- ✅ `streamlit_app.py` - Aplicação completa standalone
- ✅ `requirements_streamlit.txt` - Dependências mínimas
- ✅ `.streamlit/config.toml` - Configuração Streamlit
- ✅ `.streamlit/secrets.toml` - Secrets (não commitado)

### Funcionalidades Incluídas:
- ✅ **Autenticação completa** (registro/login)
- ✅ **Base de dados SQLite** (persistente)
- ✅ **Análise de CV com IA** (simplificada)
- ✅ **Geração de PDF**
- ✅ **Dashboard interativo**
- ✅ **Sistema de pontuação**
- ✅ **Sugestões personalizadas**

---

## 🎯 **Deploy Imediato - Streamlit Cloud**

### 1. **Preparar Repositório**:
```bash
# Adicionar ficheiros de deploy
git add streamlit_app.py requirements_streamlit.txt .streamlit/
git commit -m "Add Streamlit Cloud deploy files"
git push origin main
```

### 2. **Deploy no Streamlit Cloud**:
1. Aceder: https://share.streamlit.io
2. Login com GitHub
3. "New app" > Selecionar repositório
4. **Main file**: `streamlit_app.py`
5. Deploy!

### 3. **Resultado**:
- ✅ **Link público**: `https://[app-name].streamlit.app`
- ✅ **SSL automático** (HTTPS)
- ✅ **Atualizações automáticas** (quando fizer push)
- ✅ **Sem custos**

---

## 🧪 **Testar Localmente Primeiro**

```bash
# Instalar dependências
pip install -r requirements_streamlit.txt

# Executar aplicação
streamlit run streamlit_app.py

# Abrir: http://localhost:8501
```

### Credenciais de Teste:
- **Criar nova conta** ou
- **Username**: `demo` / **Password**: `demo123` (se existir)

---

## 🔗 **Links Úteis**

- **Streamlit Cloud**: https://share.streamlit.io
- **Documentação**: https://docs.streamlit.io/streamlit-cloud
- **GitHub Repo**: https://github.com/Ireneu99/CVmaker

---

## 🎉 **Resultado Final**

Após o deploy, terás:
- 📱 **Aplicação web completa**
- 🔗 **Link público para partilhar**
- 🔐 **Sistema de utilizadores**
- 🤖 **Análise de CV com IA**
- 📄 **Geração de PDFs**
- 💾 **Base de dados persistente**

**Tempo estimado de deploy: 5-10 minutos** ⚡

---

## 🆘 **Troubleshooting**

### Erro de Dependências:
```bash
# Verificar requirements_streamlit.txt
streamlit>=1.28.0
PyJWT>=2.8.0
reportlab>=4.0.0
```

### Erro de Ficheiro Principal:
- Confirmar que `streamlit_app.py` está na raiz
- Verificar que o ficheiro não tem erros de sintaxe

### Base de Dados:
- SQLite é criada automaticamente
- Dados persistem entre sessões no Streamlit Cloud

**🚀 Boa sorte com o deploy!**
