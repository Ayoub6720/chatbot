import streamlit as st
import random
import time
import requests
import json
import os
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(
    page_title="Chatbot Assistance Académique UHA",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Ajouter du CSS personnalisé amélioré
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #054cff, #00b3ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chat-message-user {
        background: linear-gradient(135deg, #054cff, #0066ff);
        color: white;
        margin-left: 20%;
    }
    
    .chat-message-bot {
        background: linear-gradient(135deg, #00b3ff, #0099cc);
        color: white;
        margin-right: 20%;
    }
    
   .chat-avatar {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    margin-right: 1rem;
    background-color: rgba(255,255,255,0.2);
    flex-shrink: 0;
}
    .chat-content {
        flex-grow: 1;
        line-height: 1.5;
    }
    
    .timestamp {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
    
   .welcome-card {
    padding: 1rem 2rem;
    text-align: center;
    margin: 1rem 0;
}
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-online { background-color: #28a745; }
    .status-offline { background-color: #dc3545; }
    
    .sidebar-info {
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        padding: 0.5rem;
        margin: 0.2rem 0;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .nav-item:hover {
        background-color: rgba(54, 162, 235, 0.1);
        transform: translateX(5px);
    }
    
    .nav-icon {
        font-size: 1.2rem;
        margin-right: 0.8rem;
        width: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des variables de session
def init_session_state():
    """Initialise les variables de session si elles n'existent pas"""
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "🏠 Accueil"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_status" not in st.session_state:
        st.session_state.api_status = "online"  # Simulé pour la démo

# Fonction pour appeler l'API Mistral AI (améliorée avec gestion d'erreurs)
def get_mistral_response(prompt, conversation_history=None):
    """
    Appelle l'API Mistral AI avec une gestion d'erreurs robuste
    """
    api_key = "QwSJ9Kt4P9zKtgq9iQSA2o17JAbpOJ3b"  # À déplacer vers les secrets en production
    url = "https://api.mistral.ai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Construire l'historique de conversation pour plus de contexte
    messages = [
        {
            "role": "system", 
            "content": """Vous êtes un assistant IA français spécialisé dans l'aide aux étudiants de l'Université de Haute-Alsace (UHA). 
            Vous devez :
            - Répondre de manière claire et pédagogique
            - Aider avec les questions académiques, administratives et d'orientation
            - Être empathique et encourageant
            - Fournir des informations précises sur l'université quand possible
            - Demander des clarifications si nécessaire"""
        }
    ]
    
    # Ajouter l'historique de conversation récent (5 derniers messages max)
    if conversation_history:
        recent_history = conversation_history[-10:]  # Garder les 10 derniers messages
        for msg in recent_history:
            role = "user" if msg["is_user"] else "assistant"
            messages.append({"role": role, "content": msg["content"]})
    
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": "mistral-small",  # Modèle plus performant
        "messages": messages,
        "temperature": 0.5,  # Un peu plus de créativité
        "max_tokens":500,  # Limiter la longueur des réponses
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "⏱️ Désolé, la réponse prend trop de temps. Veuillez réessayer."
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion à l'API: {str(e)}")
        return "🔧 Problème technique temporaire. Veuillez réessayer dans quelques instants."
    except KeyError:
        return "🤖 Réponse inattendue de l'API. Veuillez reformuler votre question."
    except Exception as e:
        st.error(f"Erreur inattendue: {str(e)}")
        return "❌ Une erreur s'est produite. Veuillez contacter le support technique."

# Fonction pour afficher un message avec timestamp
def display_message(message, is_user=False, timestamp=None):
    """Affiche un message dans le chat avec style amélioré"""
    avatar = "👤" if is_user else "🧠"
    message_class = "chat-message-user" if is_user else "chat-message-bot"
    
    if timestamp is None:
        timestamp = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="chat-avatar">{avatar}</div>
        <div class="chat-content">
            {message}
            <div class="timestamp">{timestamp}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Fonction pour la page Chatbot
def chatbot_page():
    """Page principale du chatbot"""
    
    # Indicateur de statut
    status_color = "status-online" if st.session_state.api_status == "online" else "status-offline"
    status_text = "En ligne" if st.session_state.api_status == "online" else "Hors ligne"
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <span class="status-indicator {status_color}"></span>
        <strong>Statut: {status_text}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Conteneur de chat
    chat_container = st.container()
    
    with chat_container:
        
        # Afficher l'historique des messages
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align: center; color: #666;">
                👋 Bonjour ! Je suis votre assistant académique UHA.<br>
                Posez-moi vos questions sur vos études, les procédures administratives, ou tout autre sujet académique !
            </div>
            """, unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            display_message(
                message["content"], 
                message["is_user"], 
                message.get("timestamp", "")
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Zone de saisie améliorée
    st.markdown("### 💭 Votre message")
    
    with st.form(key="message_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_area(
                "Tapez votre message ici...", 
                height=100,
                placeholder="Ex: Comment puis-je m'inscrire à l'UHA ?",
                key="user_input"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Espacement
            submit_button = st.form_submit_button("📤 Envoyer", use_container_width=True)
            clear_button = st.form_submit_button("🗑️ Effacer", use_container_width=True)
    
    # Traitement des actions
    if clear_button:
        st.session_state.messages = []
        st.rerun()
    
    if submit_button and user_input.strip():
        # Ajouter le message utilisateur
        timestamp = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
        st.session_state.messages.append({
            "content": user_input.strip(),
            "is_user": True,
            "timestamp": timestamp
        })
        
        # Générer la réponse du bot
        with st.spinner("🤔 Je réfléchis à votre question..."):
            if st.session_state.api_status == "online":
                bot_response = get_mistral_response(user_input, st.session_state.messages)
            else:
                bot_response = "🔧 Le service est temporairement indisponible. Veuillez réessayer plus tard."
        
        # Ajouter la réponse du bot
        bot_timestamp = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
        st.session_state.messages.append({
            "content": bot_response,
            "is_user": False,
            "timestamp": bot_timestamp
        })
        
        st.rerun()

# Pages de contenu
def accueil_page():
    """Page d'accueil améliorée"""
    st.markdown("""
    <div class="welcome-card">
        <h1>🎓 Bienvenue sur le Chatbot UHA</h1>
        <p>Votre assistant intelligent pour naviguer dans votre parcours universitaire</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 Démarrer une conversation", use_container_width=True):
            st.session_state.selected_page = "🤖 Chatbot"
            st.rerun()
    
    with col2:
        if st.button("🔐 Se connecter", use_container_width=True):
            st.session_state.selected_page = "🔐 Connexion"
            st.rerun()
    
    with col3:
        if st.button("📚 Liens utiles", use_container_width=True):
            st.session_state.selected_page = "🔗 Liens Utiles"
            st.rerun()
    
    st.markdown("---")
    
    # Fonctionnalités principales
    st.markdown("### 🚀 Que puis-je faire pour vous ?")
    
    features = [
        "📋 Renseignements sur les inscriptions et procédures",
        "📅 Informations sur les emplois du temps",
        "🎯 Aide à l'orientation et au choix de parcours",
        "📖 Support pour vos études et projets",
        "🏢 Questions administratives",
        "💡 Conseils académiques personnalisés"
    ]
    
    for feature in features:
        st.markdown(f"- {feature}")

def connexion_page():
    """Page de connexion (en développement)"""
    st.header("🔐 Connexion")
    
    # Avertissement de développement
    st.warning("⚠️ **Cette page est en cours de développement et n'est pas encore fonctionnelle.**")
    
    # Conteneur centré pour le formulaire
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 👤 Identifiants UHA")
        
        with st.form("login_form"):
            # Champs de connexion
            username = st.text_input(
                "📧 Nom d'utilisateur ou email :",
                placeholder="ex: prenom.nom@uha.fr"
            )
            
            password = st.text_input(
                "🔒 Mot de passe :",
                type="password",
                placeholder="Votre mot de passe UHA"
            )
            
            # Options supplémentaires
            remember_me = st.checkbox("Se souvenir de moi")
            
            # Bouton de connexion
            login_button = st.form_submit_button(
                "🚀 Se connecter", 
                use_container_width=True
            )
            
            if login_button:
                st.error("🚧 Fonctionnalité en développement - Connexion non disponible")
        
        # Liens utiles
        st.markdown("---")
        st.markdown("### 🔗 Liens utiles")
        st.markdown("""
        - [Portail étudiant UHA](https://e-services.uha.fr/fr/index.html)
        - [Réinitialiser mot de passe](https://e-services.uha.fr/fr/index.html)
        """)
    
    # Informations supplémentaires
    st.markdown("---")
    st.info("""
    **📋 Fonctionnalités prévues après connexion :**
    - Accès personnalisé à vos cours
    - Synchronisation avec votre planning
    - Notifications personnalisées
    - Historique de vos conversations
    """)

def liens_utiles_page():
    """Page des liens utiles"""
    st.header("🔗 Liens Utiles")
    st.info("🚧 Cette fonctionnalité est en cours de développement.")
    
    st.markdown("""
    ### 📚 Liens essentiels :
    - [Portail étudiant UHA](https://e-services.uha.fr/fr/index.html)
    - [Site officiel UHA](https://www.uha.fr/)
    - [Site officiel ENSISA](https://www.ensisa.uha.fr/)
    """)

def about_page():
    """Page À propos"""
    st.header("ℹ️ À propos")
    st.markdown("""
    ### 🎯 Mission
    Ce chatbot a été développé pour faciliter la vie étudiante à l'Université de Haute-Alsace.
    
    ### 🔧 Fonctionnalités
    - Assistant IA alimenté par Mistral AI
    - Interface utilisateur intuitive
    - Réponses contextuelles et personnalisées
    
    ### 🚀 Développement
    Version actuelle : **Beta 1.0**
    
    Ce projet est en constante évolution pour mieux servir la communauté étudiante de l'UHA. Ce bot est encore en phase de développement et la synchronisation avec la base de données universitaire n'a pas encore été effectuée.
    """)

def credits_page():
    """Page des crédits"""
    st.header("👥 Crédits")
    st.markdown("""
    ### 🏗️ Développement
    - **Développé par Ayoub**
    - **Technologie IA** : Mistral AI
    - **Framework** : Streamlit

    
    ### 📞 Contact
    Pour toute question ou suggestion : ayoub.darkaoui@uha.fr
    """)

# Application principale
def main():
    """Fonction principale de l'application"""
    init_session_state()
    
    # Logo et titre
    try:
        st.image("image_uha.png")
    except:
        st.markdown("🏫 **Université de Haute-Alsace**")
    
    # Barre latérale de navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        # Pages avec icônes
        pages = [
            "🏠 Accueil", 
            "🤖 Chatbot", 
            "🔐 Connexion", 
            "🔗 Liens Utiles", 
            "ℹ️ À Propos", 
            "👥 Crédits"
        ]
        
        # Trouver l'index de la page actuelle
        try:
            current_index = pages.index(st.session_state.selected_page)
        except ValueError:
            # Si la page actuelle n'existe pas dans la nouvelle liste, utiliser Accueil
            current_index = 0
            st.session_state.selected_page = "🏠 Accueil"
        
        selected_page = st.radio(
            "Choisir une page :",
            pages,
            index=current_index,
            key="page_selector"
        )
        
        # Détecter le changement de page et forcer le rechargement
        if selected_page != st.session_state.selected_page:
            st.session_state.selected_page = selected_page
            st.rerun()
        
        st.markdown("---")
        
        # Informations dans la sidebar
        st.markdown("""
        <div class="sidebar-info">
            <h4>💡 Conseils d'utilisation</h4>
            <p>• Soyez précis dans vos questions</p>
            <p>• N'hésitez pas à demander des clarifications</p>
            <p>• Le bot garde le contexte de conversation</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Statistiques (simulées)
        if st.session_state.messages:
            st.metric("💬 Messages échangés", len(st.session_state.messages))
    
    # Routage des pages
    page_functions = {
        "🏠 Accueil": accueil_page,
        "🤖 Chatbot": chatbot_page,
        "🔐 Connexion": connexion_page,
        "🔗 Liens Utiles": liens_utiles_page,
        "ℹ️ À Propos": about_page,
        "👥 Crédits": credits_page
    }
    
    # Afficher la page sélectionnée
    page_functions[st.session_state.selected_page]()

# Point d'entrée de l'application
if __name__ == "__main__":
    main()
