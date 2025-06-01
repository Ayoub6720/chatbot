import streamlit as st
import random
import time
import requests
import json
import os


image="image_uha.png"
# Configuration de la page
st.set_page_config(
    page_title="Chatbot Assistance Académique",
    page_icon="🤖",
    layout="centered"
)

# Ajouter du CSS personnalisé
st.markdown("""
<style>


    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
    }
    .chat-message-user {
        background-color: #054cff;
        color: white; /* Couleur du texte pour les messages utilisateur - noir */
    }
    .chat-message-bot {
        background-color: #00b3ff;
        color: white; /* Couleur du texte pour les messages du bot - vert foncé */
    }
    .chat-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .chat-content {
        flex-grow: 1;
    }
</style>
""", unsafe_allow_html=True)

# Titre de l'application
col1, col2 = st.columns([1, 10])

#st.image("image")


st.title("Chatbot de l'UHA 🤖")

#Ajout de la barre latéral
st.sidebar.title("Navigation")
selected_page = st.sidebar.radio(
    "Aller vers :", 
    ["Accueil", "Chatbot","Accès à Moodle", "À propos", "Crédits"]
)

# Contenu principal selon l'onglet sélectionné
if selected_page == "Accueil":
    st.header("Bienvenue 👋")
    st.write("Utilisez les onglets à gauche pour naviguer.")
elif selected_page == "Accès à Moodle":
    st.write("En cours de développement.")
    

elif selected_page == "Chatbot":
    
    # Fonction pour appeler l'API Mistral AI
    def get_mistral_response(prompt, api_key):
        url = "https://api.mistral.ai/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": "mistral-tiny",  # Ou un autre modèle disponible comme "mistral-small", "mistral-medium"
            "messages": [
                {"role": "system", "content": "Vous êtes un assistant IA qui permet d'assister des etudiants a l'université"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,
            
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # Vérifier les erreurs HTTP
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API Mistral: {str(e)}")
            return "Je suis désolé, je rencontre des difficultés techniques. Veuillez réessayer plus tard."

    # Configuration de la clé API
    if "api_key_configured"not in st.session_state:
        st.session_state.api_key_configured = False


    api_key = "QwSJ9Kt4P9zKtgq9iQSA2o17JAbpOJ3b"
        
     

    # Initialiser l'historique de chat s'il n'existe pas
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Fonction pour afficher un message
    def display_message(message, is_user=False):
        avatar = "👤" if is_user else "🧠"
        message_class = "chat-message-user" if is_user else "chat-message-bot"
        
        st.markdown(f"""
        <div class="chat-message {message_class}">
            <div class="chat-avatar">{avatar}</div>
            <div class="chat-content">
                {message}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Afficher l'historique des messages
    for message in st.session_state.messages:
        display_message(message["content"], message["is_user"])

    # Réponses de secours si l'API n'est pas configurée
    fallback_responses = [
        "Je vous remercie pour votre message. Pour des réponses plus intelligentes, veuillez configurer votre clé API Mistral AI.",
        "C'est une question intéressante. Je pourrais mieux y répondre si vous configurez l'API Mistral AI.",
        "Je comprends votre demande. Pour un meilleur service, veuillez configurer l'API Mistral dans la barre latérale.",
        "Merci de partager cela. Pour débloquer mes capacités, veuillez ajouter une clé API Mistral.",
        "Je suis là pour vous aider, mais mes réponses seraient plus pertinentes avec l'API Mistral configurée."
    ]

    # Zone de saisie pour l'utilisateur avec gestion du formulaire
    with st.form(key="message_form", clear_on_submit=True):
        user_input = st.text_input("Écrivez votre message ici...", key="user_input")
        submit_button = st.form_submit_button("Envoyer")

    # Traitement du message de l'utilisateur uniquement lorsque le formulaire est soumis
    if submit_button and user_input:
        # Ajouter le message de l'utilisateur à l'historique
        st.session_state.messages.append({"content": user_input, "is_user": True})
        
        # Simuler la réflexion du chatbot
        with st.spinner("En train de réfléchir..."):
            # Vérifier si l'API est configurée
            if True:
                # Obtenir la réponse de l'API Mistral
                bot_response = get_mistral_response(user_input, api_key)
            else:
                # Utiliser une réponse de secours si l'API n'est pas configurée
                time.sleep(2)  # Simuler un délai de réponse
                bot_response = random.choice(fallback_responses)
        
        # Ajouter la réponse du chatbot à l'historique
        st.session_state.messages.append({"content": bot_response, "is_user": False})
        
        # Forcer le rechargement de la page
        st.rerun()

    # Bouton pour effacer l'historique de conversation
    if st.button("Effacer la conversation"):
        st.session_state.messages = []
        st.rerun()
    
    
    

elif selected_page == "À propos":
    st.header("À propos")
    st.write("Cette application aide les étudiants à l’université.")

elif selected_page == "Crédits":
    st.header("Crédits")
    st.write("Développé par Ayoub.")
