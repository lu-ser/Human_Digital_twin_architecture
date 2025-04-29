from config.config_loader import ConfigLoader
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing import Any, Type, TypeVar, Dict, List
from llm.api_rotation.api_rotation import (
    get_llm_client,
    invalidate_cache,
    get_rotation_manager,
)

# Cache per istanza modello
_model_instance = None

T = TypeVar("T")


def get_model() -> BaseChatModel:
    """
    Ottiene l'istanza del modello LLM in base alla configurazione.
    Usa una cache per evitare di creare istanze multiple.

    Returns:
        Istanza del modello LLM
    """
    global _model_instance

    if _model_instance is None:
        config = ConfigLoader()
        provider = config.get_llm_provider()

        # Configura parametri in base al provider
        if provider == "openai":
            _model_instance = get_llm_client(
                provider="openai",
                client_class_path="langchain_openai.ChatOpenAI",
                model_name=config.get_value("llm.openai.model_name", "gpt-4o"),
                temperature=config.get_value("llm.openai.temperature", 0.1),
                max_tokens=config.get_value("llm.openai.max_tokens", 2048),
                request_timeout=config.get_value("llm.openai.timeout", 120),
            )
        elif provider == "groq":
            _model_instance = get_llm_client(
                provider="groq",
                client_class_path="langchain_groq.ChatGroq",
                model_name=config.get_value(
                    "llm.groq.model_name", "llama-3.3-70b-versatile"
                ),
                temperature=config.get_value("llm.groq.temperature", 0.1),
                max_tokens=config.get_value("llm.groq.max_tokens", 2048),
                request_timeout=config.get_value("llm.groq.timeout", 120),
            )
        else:
            # Fallback a Groq
            _model_instance = get_llm_client(
                provider="groq",
                client_class_path="langchain_groq.ChatGroq",
                model_name="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=2048,
                request_timeout=120,
            )

    return _model_instance


def reset_model_cache():
    """Resetta la cache del modello."""
    global _model_instance
    _model_instance = None
    # Invalida anche la cache della libreria di rotazione
    invalidate_cache()


def get_structured_output_parser(output_class: Type[T]):
    """
    Crea un parser per output strutturati usando Pydantic.

    Args:
        output_class: Classe Pydantic per il parsing

    Returns:
        Parser configurato
    """
    return PydanticOutputParser(pydantic_object=output_class)


def create_structured_prompt_chain(
    system_prompt: str, human_prompt: str, output_class: Type[T]
):
    """
    Crea una catena di prompt strutturata che restituisce un oggetto della classe specificata.

    Args:
        system_prompt: Prompt di sistema
        human_prompt: Prompt utente
        output_class: Classe per l'output strutturato

    Returns:
        Funzione che accetta parametri e restituisce l'output strutturato
    """
    model = get_model()
    parser = get_structured_output_parser(output_class)

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("human", human_prompt)]
    )

    chain = prompt | model | parser

    def run_chain(**kwargs):
        return chain.invoke(kwargs)

    return run_chain


def get_llm_with_structured_output(output_class: Type[T]):
    """
    Ottiene un modello LLM configurato per restituire output strutturati.

    Args:
        output_class: Classe Pydantic per il parsing

    Returns:
        LLM con output strutturato
    """
    model = get_model()
    return model.with_structured_output(output_class)
