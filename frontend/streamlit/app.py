import streamlit as st
import requests
import json
from datetime import datetime
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.settings import settings

# Configure Streamlit page
st.set_page_config(
    page_title="CV Maker Inteligente",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE_URL = f"http://localhost:8000{settings.api_v1_prefix}"

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

def make_api_request(endpoint, method="GET", data=None, headers=None):
    """Make API request with error handling."""
    url = f"{API_BASE_URL}{endpoint}"
    
    if headers is None:
        headers = {}
    
    if st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == 401:
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.error("Sessão expirada. Por favor, faça login novamente.")
            st.rerun()
        
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: {str(e)}")
        return None

def login_user(username, password):
    """Login user and store token."""
    # Send as form data for OAuth2PasswordRequestForm
    data = {
        "username": username,
        "password": password,
        "grant_type": "password"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(f"{API_BASE_URL}/auth/login", data=data, headers=headers)
    
    if response.status_code == 200:
        token_data = response.json()
        st.session_state.access_token = token_data["access_token"]
        st.session_state.authenticated = True
        
        # Get user data
        user_response = make_api_request("/auth/me")
        if user_response and user_response.status_code == 200:
            st.session_state.user_data = user_response.json()
        
        return True
    else:
        return False

def register_user(username, email, password, full_name=None):
    """Register new user."""
    data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": full_name
    }
    
    response = requests.post(f"{API_BASE_URL}/auth/register", json=data)
    return response

def logout_user():
    """Logout user."""
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.user_data = None

def show_login_page():
    """Show login/register page."""
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
                    if login_user(username, password):
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
                    else:
                        response = register_user(reg_username, reg_email, reg_password, reg_full_name)
                        if response.status_code == 200:
                            st.success("Conta criada com sucesso! Pode agora fazer login.")
                        else:
                            error_data = response.json()
                            st.error(f"Erro ao criar conta: {error_data.get('detail', 'Erro desconhecido')}")
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios!")

def show_dashboard():
    """Show main dashboard."""
    st.title("📄 Dashboard - CV Maker Inteligente")
    
    # Sidebar
    with st.sidebar:
        st.write(f"👋 Olá, {st.session_state.user_data.get('username', 'Utilizador')}!")
        
        if st.button("🚪 Logout"):
            logout_user()
            st.rerun()
        
        st.divider()
        
        # Navigation
        page = st.selectbox(
            "Navegação",
            ["Dashboard", "Meus CVs", "Criar CV", "Estatísticas", "Atividade"]
        )
    
    if page == "Dashboard":
        show_dashboard_home()
    elif page == "Meus CVs":
        show_my_cvs()
    elif page == "Criar CV":
        show_create_cv()
    elif page == "Estatísticas":
        show_statistics()
    elif page == "Atividade":
        show_activity()

def show_dashboard_home():
    """Show dashboard home page."""
    st.subheader("🏠 Início")
    
    # Get user stats
    response = make_api_request("/users/stats")
    if response and response.status_code == 200:
        stats = response.json()["data"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 CVs Criados", stats["cv_count"])
        
        with col2:
            st.metric("🔄 Total de Ações", stats["total_actions"])
        
        with col3:
            member_since = datetime.fromisoformat(stats["member_since"]).strftime("%d/%m/%Y")
            st.metric("📅 Membro desde", member_since)
        
        # Recent activity
        if stats["recent_activity"]:
            st.subheader("📊 Atividade Recente")
            for activity in stats["recent_activity"][:5]:
                timestamp = datetime.fromisoformat(activity["timestamp"]).strftime("%d/%m/%Y %H:%M")
                status_icon = "✅" if activity["status"] == "success" else "❌"
                st.write(f"{status_icon} {activity['action']} - {timestamp}")
    
    # Quick actions
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

def show_my_cvs():
    """Show user's CVs."""
    st.subheader("📋 Meus CVs")
    
    response = make_api_request("/cv/")
    if response and response.status_code == 200:
        cvs = response.json()
        
        if not cvs:
            st.info("Ainda não tem CVs criados. Crie o seu primeiro CV!")
            if st.button("➕ Criar Primeiro CV"):
                st.session_state.page = "Criar CV"
                st.rerun()
        else:
            for cv in cvs:
                with st.expander(f"📄 {cv['title']} (Score: {cv.get('analysis_score', 'N/A')}/100)"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Criado:** {datetime.fromisoformat(cv['created_at']).strftime('%d/%m/%Y')}")
                        st.write(f"**Setor:** {cv.get('sector', 'Não especificado')}")
                    
                    with col2:
                        if st.button(f"🔍 Analisar", key=f"analyze_{cv['id']}"):
                            analyze_cv(cv['id'])
                        
                        if st.button(f"📄 Gerar PDF", key=f"pdf_{cv['id']}"):
                            generate_pdf(cv['id'])
                    
                    with col3:
                        if cv.get('pdf_path'):
                            if st.button(f"⬇️ Download PDF", key=f"download_{cv['id']}"):
                                download_pdf(cv['id'])
                        
                        if st.button(f"🗑️ Eliminar", key=f"delete_{cv['id']}"):
                            delete_cv(cv['id'])
                    
                    # Show suggestions if available
                    if cv.get('suggestions'):
                        st.write("**Sugestões de Melhoria:**")
                        for suggestion in cv['suggestions'][:3]:  # Show first 3 suggestions
                            priority_color = "🔴" if suggestion['priority'] == 'high' else "🟡" if suggestion['priority'] == 'medium' else "🔵"
                            st.write(f"{priority_color} {suggestion['title']}: {suggestion['description']}")

def show_create_cv():
    """Show create CV page."""
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
        
        submit_cv = st.form_submit_button("📤 Criar CV")
        
        if submit_cv:
            if title and cv_text:
                data = {
                    "title": title,
                    "original_text": cv_text,
                    "sector": sector if sector else None
                }
                
                response = make_api_request("/cv/upload", method="POST", data=data)
                if response and response.status_code == 200:
                    result = response.json()
                    st.success(f"CV '{title}' criado com sucesso!")
                    
                    # Auto-analyze the CV
                    cv_id = result["data"]["cv_id"]
                    st.info("A analisar o CV automaticamente...")
                    analyze_cv(cv_id)
                else:
                    st.error("Erro ao criar CV!")
            else:
                st.error("Por favor, preencha todos os campos!")

def analyze_cv(cv_id):
    """Analyze CV and show results."""
    response = make_api_request(f"/cv/{cv_id}/analyze", method="POST")
    if response and response.status_code == 200:
        result = response.json()
        
        st.success("✅ CV analisado com sucesso!")
        
        # Show score
        score = result["analysis_score"]
        score_color = "green" if score >= 70 else "orange" if score >= 50 else "red"
        st.markdown(f"**Pontuação:** :{score_color}[{score}/100]")
        
        # Show suggestions
        if result["suggestions"]:
            st.subheader("💡 Sugestões de Melhoria")
            for i, suggestion in enumerate(result["suggestions"], 1):
                priority_icon = "🔴" if suggestion['priority'] == 'high' else "🟡" if suggestion['priority'] == 'medium' else "🔵"
                
                with st.expander(f"{priority_icon} {i}. {suggestion['title']}"):
                    st.write(suggestion['description'])
                    if suggestion.get('examples'):
                        st.write("**Exemplos:**")
                        for example in suggestion['examples']:
                            st.write(f"• {example}")
        
        # Show keywords
        if result["keywords"]:
            st.subheader("🔑 Palavras-chave Identificadas")
            st.write(", ".join(result["keywords"][:10]))
    else:
        st.error("Erro ao analisar CV!")

def generate_pdf(cv_id):
    """Generate PDF for CV."""
    response = make_api_request(f"/cv/{cv_id}/generate-pdf", method="POST")
    if response and response.status_code == 200:
        st.success("✅ PDF gerado com sucesso!")
        st.info("Pode agora fazer o download do PDF.")
    else:
        st.error("Erro ao gerar PDF!")

def download_pdf(cv_id):
    """Download CV PDF."""
    response = make_api_request(f"/cv/{cv_id}/download-pdf")
    if response and response.status_code == 200:
        st.download_button(
            label="⬇️ Download PDF",
            data=response.content,
            file_name=f"cv_{cv_id}.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Erro ao fazer download do PDF!")

def delete_cv(cv_id):
    """Delete CV."""
    if st.button("Confirmar eliminação", key=f"confirm_delete_{cv_id}"):
        response = make_api_request(f"/cv/{cv_id}", method="DELETE")
        if response and response.status_code == 200:
            st.success("CV eliminado com sucesso!")
            st.rerun()
        else:
            st.error("Erro ao eliminar CV!")

def show_statistics():
    """Show user statistics."""
    st.subheader("📊 Estatísticas")
    
    response = make_api_request("/users/stats")
    if response and response.status_code == 200:
        stats = response.json()["data"]
        
        # Display detailed stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📄 Total de CVs", stats["cv_count"])
            st.metric("🔄 Total de Ações", stats["total_actions"])
        
        with col2:
            member_since = datetime.fromisoformat(stats["member_since"])
            days_member = (datetime.now() - member_since).days
            st.metric("📅 Dias como membro", days_member)
        
        # Activity chart (simplified)
        if stats["recent_activity"]:
            st.subheader("📈 Atividade Recente")
            activity_data = {}
            for activity in stats["recent_activity"]:
                action = activity["action"]
                activity_data[action] = activity_data.get(action, 0) + 1
            
            st.bar_chart(activity_data)

def show_activity():
    """Show user activity log."""
    st.subheader("📋 Registo de Atividade")
    
    response = make_api_request("/users/activity")
    if response and response.status_code == 200:
        activity_data = response.json()["data"]
        activities = activity_data["activity"]
        
        if activities:
            for activity in activities:
                timestamp = datetime.fromisoformat(activity["timestamp"]).strftime("%d/%m/%Y %H:%M:%S")
                status_icon = "✅" if activity["status"] == "success" else "❌"
                
                with st.expander(f"{status_icon} {activity['action']} - {timestamp}"):
                    st.write(f"**Status:** {activity['status']}")
                    if activity.get('execution_time'):
                        st.write(f"**Tempo de execução:** {activity['execution_time']}ms")
                    if activity.get('details'):
                        st.write(f"**Detalhes:** {activity['details']}")
        else:
            st.info("Nenhuma atividade registada.")

# Main app logic
def main():
    """Main application logic."""
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
