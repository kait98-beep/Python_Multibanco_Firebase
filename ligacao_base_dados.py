import firebase_admin
from firebase_admin import credentials, firestore

def ligar_base_dados():
    """Liga ao Firebase com a chave guardada em "chave.json".

    Returns:
        firestore.Client: cliente usado para aceder à base de dados.
    """
    # Ligar ao Firebase
    cred = credentials.Certificate("chave.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    return db

db = ligar_base_dados()

