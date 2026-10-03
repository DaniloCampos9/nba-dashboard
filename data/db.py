import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega as variáveis do seu arquivo .env
load_dotenv()

# st.cache_resource garante que a conexão abra apenas 1 vez e fique na memória
@st.cache_resource
def init_connection() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        st.error("⚠️ Credenciais do Supabase não encontradas no arquivo .env!")
        st.stop()
    return create_client(url, key)

# Objeto global para importar nos outros arquivos
supabase = init_connection()