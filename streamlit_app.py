"""
CV Maker Inteligente - Versão Streamlit Cloud
Aplicação completa que roda inteiramente no Streamlit Cloud
"""

import streamlit as st
import sqlite3
import hashlib
import jwt
import datetime
import os
import sys
import json
import re
from pathlib import Path
import tempfile
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Configuração da página
st.set_page_config(
    page_title="CV Maker Inteligente",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações
SECRET_KEY = "cv-maker-secret-key-for-streamlit-cloud-deployment-2024"
DATABASE_FILE = "cvmaker_cloud.db"

# Inicialização da base de dados
def init_database():
    """Inicializar base de dados SQLite."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Criar tabela de utilizadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Criar tabela de CVs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cvs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            original_text TEXT NOT NULL,
            analyzed_text TEXT,
            analysis_score INTEGER,
            suggestions TEXT,
            keywords TEXT,
            sector TEXT,
            pdf_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Criar tabela de logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'success'
        )
    ''')
    
    conn.commit()
    conn.close()

# Funções de autenticação
def hash_password(password):
    """Hash da password."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verificar password."""
    return hash_password(password) == hashed

def create_token(username):
    """Criar JWT token."""
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verificar JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except:
        return None

# Funções de base de dados
def create_user(username, email, password, full_name=None):
    """Criar novo utilizador."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, full_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    """Autenticar utilizador."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and verify_password(password, result[0]):
        return True
    return False

def get_user_data(username):
    """Obter dados do utilizador."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'username': result[1],
            'email': result[2],
            'full_name': result[4],
            'created_at': result[5]
        }
    return None

# Análise de CV simplificada
def analyze_cv_simple(text, sector=None):
    """Análise simplificada de CV."""
    score = 50  # Score base
    suggestions = []
    keywords = []
    
    # Verificações básicas
    if len(text) < 100:
        suggestions.append({
            'title': 'CV muito curto',
            'description': 'O seu CV parece muito curto. Adicione mais detalhes sobre a sua experiência.',
            'priority': 'high'
        })
        score -= 20
    
    # Verificar contactos
    if '@' in text:
        score += 10
        keywords.append('email')
    else:
        suggestions.append({
            'title': 'Adicionar email',
            'description': 'Inclua o seu endereço de email para contacto.',
            'priority': 'high'
        })
    
    # Verificar telefone
    if re.search(r'\+?\d{9,}', text):
        score += 10
        keywords.append('telefone')
    else:
        suggestions.append({
            'title': 'Adicionar telefone',
            'description': 'Inclua o seu número de telefone.',
            'priority': 'medium'
        })
    
    # Verificar experiência
    exp_words = ['experiência', 'trabalho', 'empresa', 'função', 'cargo', 'responsabilidades']
    if any(word in text.lower() for word in exp_words):
        score += 15
        keywords.extend(['experiência', 'trabalho'])
    else:
        suggestions.append({
            'title': 'Adicionar experiência profissional',
            'description': 'Inclua detalhes sobre a sua experiência de trabalho.',
            'priority': 'high'
        })
    
    # Verificar educação
    edu_words = ['educação', 'formação', 'curso', 'universidade', 'licenciatura', 'mestrado']
    if any(word in text.lower() for word in edu_words):
        score += 15
        keywords.extend(['educação', 'formação'])
    else:
        suggestions.append({
            'title': 'Adicionar formação académica',
            'description': 'Inclua informações sobre a sua educação e formação.',
            'priority': 'medium'
        })
    
    # Verificar competências
    skill_words = ['competências', 'skills', 'habilidades', 'conhecimentos']
    if any(word in text.lower() for word in skill_words):
        score += 10
        keywords.extend(['competências', 'skills'])
    else:
        suggestions.append({
            'title': 'Adicionar competências',
            'description': 'Liste as suas competências técnicas e pessoais.',
            'priority': 'medium'
        })
    
    # Verificar verbos de ação
    action_verbs = ['desenvolvi', 'implementei', 'geri', 'liderei', 'criei', 'melhorei', 'aumentei']
    if any(verb in text.lower() for verb in action_verbs):
        score += 10
        keywords.append('verbos de ação')
    else:
        suggestions.append({
            'title': 'Usar verbos de ação',
            'description': 'Use verbos de ação para descrever as suas conquistas (ex: desenvolvi, implementei, geri).',
            'priority': 'medium'
        })
    
    # Verificar quantificação
    if re.search(r'\d+%|\d+\s*(anos?|meses?)', text):
        score += 10
        keywords.append('quantificação')
    else:
        suggestions.append({
            'title': 'Quantificar resultados',
            'description': 'Inclua números e percentagens para quantificar os seus resultados.',
            'priority': 'medium'
        })
    
    # Ajustar score por setor
    if sector:
        keywords.append(f'setor_{sector}')
        if sector == 'tecnologia':
            tech_words = ['python', 'javascript', 'sql', 'git', 'api', 'web', 'mobile']
            if any(word in text.lower() for word in tech_words):
                score += 5
        elif sector == 'marketing':
            marketing_words = ['campanha', 'digital', 'social media', 'analytics', 'roi']
            if any(word in text.lower() for word in marketing_words):
                score += 5
    
    # Garantir que o score está entre 0 e 100
    score = max(0, min(100, score))
    
    return {
        'score': score,
        'suggestions': suggestions,
        'keywords': keywords[:10]  # Limitar a 10 keywords
    }

def save_cv(user_id, title, original_text, analysis_result, sector=None):
    """Guardar CV na base de dados."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO cvs (user_id, title, original_text, analysis_score, suggestions, keywords, sector)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        title,
        original_text,
        analysis_result['score'],
        json.dumps(analysis_result['suggestions']),
        json.dumps(analysis_result['keywords']),
        sector
    ))
    
    cv_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return cv_id

def get_user_cvs(user_id):
    """Obter CVs do utilizador."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, analysis_score, sector, created_at, suggestions, keywords
        FROM cvs WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    cvs = []
    for row in results:
        cv = {
            'id': row[0],
            'title': row[1],
            'analysis_score': row[2],
            'sector': row[3],
            'created_at': row[4],
            'suggestions': json.loads(row[5]) if row[5] else [],
            'keywords': json.loads(row[6]) if row[6] else []
        }
        cvs.append(cv)
    
    return cvs

def get_cv_details(cv_id, user_id):
    """Obter detalhes de um CV específico."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM cvs WHERE id = ? AND user_id = ?
    ''', (cv_id, user_id))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'title': result[2],
            'original_text': result[3],
            'analysis_score': result[5],
            'suggestions': json.loads(result[6]) if result[6] else [],
            'keywords': json.loads(result[7]) if result[7] else [],
            'sector': result[8],
            'created_at': result[10]
        }
    return None

def generate_pdf(cv_data):
    """Gerar PDF do CV."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor='#2E86AB'
    )
    story.append(Paragraph(cv_data['title'], title_style))
    story.append(Spacer(1, 12))
    
    # Conteúdo do CV
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        leading=14
    )
    
    # Dividir o texto em parágrafos
    paragraphs = cv_data['original_text'].split('\n\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip(), content_style))
            story.append(Spacer(1, 6))
    
    # Adicionar score
    score_style = ParagraphStyle(
        'Score',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#666666',
        spaceAfter=12
    )
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Score de Qualidade: {cv_data['analysis_score']}/100", score_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Interface Streamlit
def main():
    """Função principal da aplicação."""
    # Inicializar base de dados
    init_database()
    
    # Estado da sessão
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    
    # Verificar autenticação
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_dashboard()

def show_auth_page():
    """Mostrar página de autenticação."""
    st.title("🔐 CV Maker Inteligente")
    st.markdown("### Bem-vindo à plataforma de criação de CVs com IA")
    
    tab1, tab2 = st.tabs(["Login", "Registar"])
    
    with tab1:
        st.subheader("Fazer Login")
        with st.form("login_form"):
            username = st.text_input("Nome de utilizador")
            password = st.text_input("Palavra-passe", type="password")
            submit_login = st.form_submit_button("Entrar")
            
            if submit_login:
                if username and password:
                    if authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_data = get_user_data(username)
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas!")
                else:
                    st.error("Por favor, preencha todos os campos!")
    
    with tab2:
        st.subheader("Criar Conta")
        with st.form("register_form"):
            reg_username = st.text_input("Nome de utilizador", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_full_name = st.text_input("Nome completo (opcional)", key="reg_full_name")
            reg_password = st.text_input("Palavra-passe", type="password", key="reg_password")
            reg_password_confirm = st.text_input("Confirmar palavra-passe", type="password", key="reg_password_confirm")
            submit_register = st.form_submit_button("Registar")
            
            if submit_register:
                if reg_username and reg_email and reg_password:
                    if reg_password != reg_password_confirm:
                        st.error("As palavras-passe não coincidem!")
                    elif len(reg_password) < 6:
                        st.error("A palavra-passe deve ter pelo menos 6 caracteres!")
                    else:
                        if create_user(reg_username, reg_email, reg_password, reg_full_name):
                            st.success("Conta criada com sucesso! Pode agora fazer login.")
                        else:
                            st.error("Erro ao criar conta. Nome de utilizador ou email já existem.")
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios!")

def show_dashboard():
    """Mostrar dashboard principal."""
    st.title("📄 Dashboard - CV Maker Inteligente")
    
    # Sidebar
    with st.sidebar:
        st.write(f"👋 Olá, {st.session_state.user_data['username']}!")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_data = None
            st.rerun()
        
        st.divider()
        
        # Navigation
        page = st.selectbox(
            "Navegação",
            ["Dashboard", "Meus CVs", "Criar CV"]
        )
    
    if page == "Dashboard":
        show_dashboard_home()
    elif page == "Meus CVs":
        show_my_cvs()
    elif page == "Criar CV":
        show_create_cv()

def show_dashboard_home():
    """Mostrar página inicial do dashboard."""
    st.subheader("🏠 Início")
    
    user_id = st.session_state.user_data['id']
    cvs = get_user_cvs(user_id)
    
    # Estatísticas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📄 CVs Criados", len(cvs))
    
    with col2:
        avg_score = sum(cv['analysis_score'] for cv in cvs) / len(cvs) if cvs else 0
        st.metric("📊 Score Médio", f"{avg_score:.1f}/100")
    
    with col3:
        member_since = st.session_state.user_data['created_at'][:10]
        st.metric("📅 Membro desde", member_since)
    
    # Ações rápidas
    st.subheader("🚀 Ações Rápidas")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Criar Novo CV", use_container_width=True):
            st.session_state.page = "Criar CV"
            st.rerun()
    
    with col2:
        if st.button("📋 Ver Meus CVs", use_container_width=True):
            st.session_state.page = "Meus CVs"
            st.rerun()
    
    # CVs recentes
    if cvs:
        st.subheader("📋 CVs Recentes")
        for cv in cvs[:3]:  # Mostrar apenas os 3 mais recentes
            with st.expander(f"📄 {cv['title']} (Score: {cv['analysis_score']}/100)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Criado:** {cv['created_at'][:10]}")
                    if cv['sector']:
                        st.write(f"**Setor:** {cv['sector']}")
                with col2:
                    if st.button(f"📄 Ver Detalhes", key=f"view_{cv['id']}"):
                        st.session_state.selected_cv = cv['id']

def show_my_cvs():
    """Mostrar CVs do utilizador."""
    st.subheader("📋 Meus CVs")
    
    user_id = st.session_state.user_data['id']
    cvs = get_user_cvs(user_id)
    
    if not cvs:
        st.info("Ainda não tem CVs criados. Crie o seu primeiro CV!")
        if st.button("➕ Criar Primeiro CV"):
            st.session_state.page = "Criar CV"
            st.rerun()
    else:
        for cv in cvs:
            with st.expander(f"📄 {cv['title']} (Score: {cv['analysis_score']}/100)"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Criado:** {cv['created_at'][:10]}")
                    if cv['sector']:
                        st.write(f"**Setor:** {cv['sector']}")
                
                with col2:
                    if st.button(f"📄 Gerar PDF", key=f"pdf_{cv['id']}"):
                        cv_details = get_cv_details(cv['id'], user_id)
                        if cv_details:
                            pdf_buffer = generate_pdf(cv_details)
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=pdf_buffer.getvalue(),
                                file_name=f"{cv['title']}.pdf",
                                mime="application/pdf",
                                key=f"download_{cv['id']}"
                            )
                
                with col3:
                    if st.button(f"🔍 Ver Detalhes", key=f"details_{cv['id']}"):
                        show_cv_details(cv['id'])
                
                # Mostrar sugestões
                if cv['suggestions']:
                    st.write("**Sugestões de Melhoria:**")
                    for i, suggestion in enumerate(cv['suggestions'][:3]):
                        priority_color = "🔴" if suggestion['priority'] == 'high' else "🟡" if suggestion['priority'] == 'medium' else "🔵"
                        st.write(f"{priority_color} {suggestion['title']}: {suggestion['description']}")

def show_cv_details(cv_id):
    """Mostrar detalhes de um CV."""
    user_id = st.session_state.user_data['id']
    cv = get_cv_details(cv_id, user_id)
    
    if cv:
        st.subheader(f"📄 {cv['title']}")
        
        # Score
        score_color = "green" if cv['analysis_score'] >= 70 else "orange" if cv['analysis_score'] >= 50 else "red"
        st.markdown(f"**Pontuação:** :{score_color}[{cv['analysis_score']}/100]")
        
        # Conteúdo
        st.subheader("📝 Conteúdo do CV")
        st.text_area("", value=cv['original_text'], height=300, disabled=True)
        
        # Sugestões
        if cv['suggestions']:
            st.subheader("💡 Sugestões de Melhoria")
            for i, suggestion in enumerate(cv['suggestions'], 1):
                priority_icon = "🔴" if suggestion['priority'] == 'high' else "🟡" if suggestion['priority'] == 'medium' else "🔵"
                
                with st.expander(f"{priority_icon} {i}. {suggestion['title']}"):
                    st.write(suggestion['description'])
        
        # Keywords
        if cv['keywords']:
            st.subheader("🔑 Palavras-chave Identificadas")
            st.write(", ".join(cv['keywords']))

def show_create_cv():
    """Mostrar página de criação de CV."""
    st.subheader("➕ Criar Novo CV")
    
    with st.form("create_cv_form"):
        title = st.text_input("Título do CV", value="Meu CV")
        sector = st.selectbox(
            "Setor Profissional",
            ["", "tecnologia", "marketing", "vendas", "recursos_humanos", "financas", "outros"]
        )
        
        cv_text = st.text_area(
            "Conteúdo do CV",
            height=400,
            placeholder="""Exemplo:
Nome: João Silva
Email: joao.silva@email.com
Telefone: +351 123 456 789

Objetivo:
Profissional de tecnologia com 5 anos de experiência...

Experiência Profissional:
- Desenvolvedor Python na Empresa XYZ (2020-2023)
  - Desenvolvi aplicações web usando Django
  - Implementei APIs REST
  - Melhorei performance em 30%

Educação:
- Licenciatura em Engenharia Informática - Universidade ABC (2018)

Competências:
- Python, JavaScript, SQL
- Django, React, PostgreSQL
- Git, Docker, AWS"""
        )
        
        submit_cv = st.form_submit_button("📤 Criar e Analisar CV")
        
        if submit_cv:
            if title and cv_text:
                # Analisar CV
                with st.spinner("A analisar o CV..."):
                    analysis_result = analyze_cv_simple(cv_text, sector if sector else None)
                
                # Guardar CV
                user_id = st.session_state.user_data['id']
                cv_id = save_cv(user_id, title, cv_text, analysis_result, sector if sector else None)
                
                st.success(f"✅ CV '{title}' criado e analisado com sucesso!")
                
                # Mostrar resultados
                score = analysis_result['score']
                score_color = "green" if score >= 70 else "orange" if score >= 50 else "red"
                st.markdown(f"**Pontuação:** :{score_color}[{score}/100]")
                
                # Mostrar sugestões
                if analysis_result['suggestions']:
                    st.subheader("💡 Sugestões de Melhoria")
                    for i, suggestion in enumerate(analysis_result['suggestions'], 1):
                        priority_icon = "🔴" if suggestion['priority'] == 'high' else "🟡" if suggestion['priority'] == 'medium' else "🔵"
                        
                        with st.expander(f"{priority_icon} {i}. {suggestion['title']}"):
                            st.write(suggestion['description'])
                
                # Mostrar keywords
                if analysis_result['keywords']:
                    st.subheader("🔑 Palavras-chave Identificadas")
                    st.write(", ".join(analysis_result['keywords']))
                
                # Botão para gerar PDF
                if st.button("📄 Gerar PDF"):
                    cv_details = get_cv_details(cv_id, user_id)
                    if cv_details:
                        pdf_buffer = generate_pdf(cv_details)
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_buffer.getvalue(),
                            file_name=f"{title}.pdf",
                            mime="application/pdf"
                        )
            else:
                st.error("Por favor, preencha todos os campos!")

# Executar aplicação
if __name__ == "__main__":
    main()
