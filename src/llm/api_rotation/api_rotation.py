import importlib
import os
from typing import Dict, Any, Type, Optional
from dotenv import load_dotenv

# Cache delle istanze
_llm_instances_cache = {}
_rotation_manager = None


def get_llm_client(provider: str, client_class_path: str, **kwargs) -> Any:
    """
    Ottiene un client LLM, utilizzando una cache per evitare la creazione di istanze multiple.

    Args:
        provider: Nome del provider LLM (es. "openai", "groq")
        client_class_path: Percorso alla classe client LangChain (es. "langchain_openai.ChatOpenAI")
        **kwargs: Parametri aggiuntivi per l'istanziazione del client

    Returns:
        Istanza client LLM
    """
    global _llm_instances_cache

    # Crea una chiave cache basata sui parametri
    cache_key = f"{provider}|{client_class_path}|{str(sorted(kwargs.items()))}"

    # Se l'istanza è già nella cache, restituiscila
    if cache_key in _llm_instances_cache:
        return _llm_instances_cache[cache_key]

    # Assicurati che le API key siano caricate
    load_dotenv("config/.env", override=True)

    # Dinamicamente importa e istanzia la classe client
    module_path, class_name = client_class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    client_class = getattr(module, class_name)

    # Controlla se ci sono API key disponibili per la rotazione
    rotation_manager = get_rotation_manager()
    if rotation_manager and provider in rotation_manager.get_available_providers():
        # Usa l'API key dal rotation manager
        api_key = rotation_manager.get_api_key(provider)
        if api_key:
            if provider == "openai":
                kwargs["api_key"] = api_key
            elif provider == "groq":
                kwargs["api_key"] = api_key

    # Crea l'istanza del client
    client = client_class(**kwargs)

    # Aggiungi l'istanza alla cache
    _llm_instances_cache[cache_key] = client

    return client


def invalidate_cache():
    """
    Invalida la cache delle istanze LLM
    """
    global _llm_instances_cache
    _llm_instances_cache = {}


class ApiRotationManager:
    """
    Gestisce la rotazione delle API keys tra diversi provider
    """

    def __init__(self):
        self.providers = {
            "openai": self._load_api_keys("OPENAI_API_KEY"),
            "groq": self._load_api_keys("GROQ_API_KEY"),
        }
        self.current_index = {provider: 0 for provider in self.providers}

    def _load_api_keys(self, env_var_prefix: str) -> list:
        """
        Carica API keys dalle variabili d'ambiente

        Args:
            env_var_prefix: Prefisso della variabile d'ambiente

        Returns:
            Lista di API keys
        """
        # Cerca API key singola
        api_key = os.getenv(env_var_prefix)
        if api_key:
            return [api_key]

        # Cerca API keys multiple (es. OPENAI_API_KEY_1, OPENAI_API_KEY_2, ecc.)
        keys = []
        i = 1
        while True:
            key = os.getenv(f"{env_var_prefix}_{i}")
            if not key:
                break
            keys.append(key)
            i += 1

        return keys

    def get_available_providers(self) -> list:
        """
        Restituisce una lista di provider disponibili con API keys valide

        Returns:
            Lista di provider disponibili
        """
        return [provider for provider, keys in self.providers.items() if keys]

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Ottiene la prossima API key per il provider specificato

        Args:
            provider: Nome del provider

        Returns:
            API key o None se non disponibile
        """
        if provider not in self.providers or not self.providers[provider]:
            return None

        keys = self.providers[provider]
        key = keys[self.current_index[provider]]

        # Aggiorna l'indice per la rotazione
        self.current_index[provider] = (self.current_index[provider] + 1) % len(keys)

        return key


def get_rotation_manager() -> ApiRotationManager:
    """
    Ottiene l'istanza del gestore rotazione API

    Returns:
        Istanza ApiRotationManager
    """
    global _rotation_manager

    if _rotation_manager is None:
        _rotation_manager = ApiRotationManager()

    return _rotation_manager
