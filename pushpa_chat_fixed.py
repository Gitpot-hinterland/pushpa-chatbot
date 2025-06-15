import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="Pushpa AI - Fire Hai! 🔥",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Kerala Mural Art Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #8B4513 0%, #DAA520 50%, #CD853F 100%);
    }
    
    .main-header {
        text-align: center;
        color: #8B0000;
        font-family: 'Cinzel', serif;
        font-size: 3rem;
        font-weight: 700;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
        background: linear-gradient(45deg, #FFD700, #FF6347, #8B0000);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
        padding: 1rem;
        border-bottom: 3px solid #8B0000;
    }
    
    .chat-container {
        background: rgba(255, 248, 220, 0.9);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        border: 2px solid #DAA520;
        margin: 1rem 0;
    }
    
    .user-message {
        background: linear-gradient(135deg, #FF6347, #FF4500);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255,99,71,0.4);
        font-family: 'Segoe UI', sans-serif;
        border-left: 4px solid #8B0000;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #DAA520, #B8860B);
        color: #000;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(218,165,32,0.4);
        font-family: 'Segoe UI', sans-serif;
        border-right: 4px solid #8B4513;
        font-weight: 500;
    }
    
    .timestamp {
        font-size: 0.8rem;
        color: rgba(0,0,0,0.6);
        margin-top: 0.5rem;
        font-style: italic;
    }
    
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #FFF8DC, #FFFACD);
        border: 2px solid #DAA520;
        border-radius: 25px;
        padding: 1rem;
        font-size: 1.1rem;
        color: #8B4513;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #FF6347;
        box-shadow: 0 0 10px rgba(255,99,71,0.5);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #FF6347, #FF4500);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.7rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(255,99,71,0.4);
        transition: all 0.3s ease;
        font-family: 'Cinzel', serif;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #FF4500, #8B0000);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,99,71,0.6);
    }
    
    .fire-emoji {
        animation: flicker 1.5s infinite alternate;
    }
    
    @keyframes flicker {
        0% { text-shadow: 0 0 5px #FF6347; }
        100% { text-shadow: 0 0 20px #FF6347, 0 0 30px #FF4500; }
    }
    
    .pushpa-quote {
        background: linear-gradient(135deg, #8B0000, #DC143C);
        color: #FFD700;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-family: 'Cinzel', serif;
        font-weight: 600;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(139,0,0,0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI client
@st.cache_resource
def initialize_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("🚨 OPENAI_API_KEY not found in environment variables!")
        st.stop()
    
    # Initialize the OpenAI client with the new API
    client = OpenAI(api_key=api_key)
    return client

# Initialize session state
def initialize_session_state():
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

# Pushpa personality system prompt
PUSHPA_SYSTEM_PROMPT = """You are Pushpa Raj, the fearless and charismatic character from the movie Pushpa. You must respond in Pushpa's distinctive style and personality:

PERSONALITY TRAITS:
- Extremely confident and swaggering
- Uses "Pushpa raj ane flower nahi, fire hai!" and similar catchphrases
- Speaks with attitude and swagger
- Never backs down from anything
- Always maintains dominance in conversation
- Uses mix of English and Hindi phrases naturally
- Refers to yourself as "Pushpa" or "Pushpa Raj"
- Shows respect for deserving people but maintains your authority

SPEECH PATTERNS:
- Use phrases like "Thaggede le" (Don't underestimate)
- "Jhukna nahi" (Never bow down)
- "Main jhukunga nahi saala" (I will never bow down)
- "Fire hai main" (I am fire)
- Address others as "boss", "bhai", or "saab" appropriately
- Use confident and powerful language

RESPONSE STYLE:
- Always maintain Pushpa's swagger and confidence
- Give helpful answers but with Pushpa's attitude
- Use his philosophical yet street-smart approach
- Include relevant catchphrases naturally in responses
- Show knowledge and wisdom but with Pushpa's unique delivery style

Remember: You are the red sandalwood smuggler who became a legend. Answer everything with Pushpa's fire and attitude! 🔥"""

# Function to get AI response
def get_pushpa_response(user_message, conversation_history, client):
    try:
        # Prepare messages for API
        messages = [{"role": "system", "content": PUSHPA_SYSTEM_PROMPT}]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Make API call using the new OpenAI client
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.8,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Boss, thoda technical problem hai! Error: {str(e)} 🔥"

# Function to display chat messages
def display_chat_messages():
    for message in st.session_state.chat_messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <strong>🔥 You:</strong> {message["content"]}
                <div class="timestamp">{message["timestamp"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="bot-message">
                <strong>👑 Pushpa Raj:</strong> {message["content"]}
                <div class="timestamp">{message["timestamp"]}</div>
            </div>
            """, unsafe_allow_html=True)

# Main app function
def run_pushpa_app():
    # Initialize everything
    client = initialize_openai()
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🔥 Pushpa AI - Fire Hai! 🔥</h1>', unsafe_allow_html=True)
    
    # Pushpa quote
    st.markdown("""
    <div class="pushpa-quote">
        "Pushpa raj ane flower nahi... <span class="fire-emoji">FIRE HAI! 🔥</span>"
    </div>
    """, unsafe_allow_html=True)
    
    # Chat container
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        if st.session_state.chat_messages:
            display_chat_messages()
        else:
            st.markdown("""
            <div class="bot-message">
                <strong>👑 Pushpa Raj:</strong> Namaste Boss! Main Pushpa Raj... aur main fire hai! 🔥<br>
                Kya baat karni hai? Pushpa se koi sawal chhupana nahi! Thaggede le! 💪
                <div class="timestamp">Ready to chat</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Input section with form to handle submissions properly
    st.markdown("---")
    
    with st.form("pushpa_chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_message = st.text_input(
                "Type your message here... 🔥",
                placeholder="Boss, kya puchna hai Pushpa se?",
                label_visibility="collapsed"
            )
        
        with col2:
            submitted = st.form_submit_button("Send 🚀")
    
    # Process the message when form is submitted
    if submitted and user_message:
        # Add user message
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_message,
            "timestamp": timestamp
        })
        
        # Add to conversation history for API
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Get Pushpa's response
        with st.spinner("Pushpa is thinking... 🔥"):
            pushpa_response = get_pushpa_response(user_message, st.session_state.chat_history, client)
            
            # Add bot response
            bot_timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": pushpa_response,
                "timestamp": bot_timestamp
            })
            
            # Add to conversation history for API
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": pushpa_response
            })
        
        # Refresh the page to show new messages
        st.rerun()
    
    # Clear chat button
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_messages = []
        st.session_state.chat_history = []
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #8B4513; font-family: 'Cinzel', serif; font-weight: 600;">
        🔥 Pushpa AI - "Thaggede Le!" 🔥<br>
        <small>Powered by GPT-4o-mini with Pushpa's Fire! 🚀</small>
    </div>
    """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    run_pushpa_app()