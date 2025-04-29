from typing import Dict, Any, List


class PromptTemplates:
    """
    Template di prompt per diverse operazioni LLM nel sistema HDT
    """

    @staticmethod
    def triplet_extraction_prompt(text: str) -> str:
        """
        Crea un prompt per estrarre triplet di conoscenza da testo

        Args:
            text: Testo di input

        Returns:
            Prompt formattato
        """
        return f"""
        Estrai triplet di conoscenza dal seguente testo. Un triplet è composto da un soggetto, un predicato e un oggetto.
        
        Esempio:
        Testo: "John likes pizza and lives in New York."
        Triplet 1: (John, likes, pizza)
        Triplet 2: (John, lives in, New York)
        
        Testo: {text}
        
        Estrai tutti i triplet in formato (soggetto, predicato, oggetto):
        """

    @staticmethod
    def knowledge_graph_analysis_prompt(
        knowledge_graph: Dict[str, Any],
        profile_data: Dict[str, Any] = None,
        physiological_data: Dict[str, Any] = None,
        calendar_data: Dict[str, Any] = None,
    ) -> str:
        """
        Crea un prompt per analizzare il knowledge graph per trigger di intervento

        Args:
            knowledge_graph: Knowledge graph dall'HDT
            profile_data: Dati profilo opzionali
            physiological_data: Dati fisiologici opzionali
            calendar_data: Dati calendario opzionali

        Returns:
            Prompt formattato
        """
        # Converti knowledge graph in rappresentazione testuale
        kg_text = ""
        for triplet_id, data in knowledge_graph.items():
            triplet = data["triplet"]
            sources = ", ".join(data["sources"])
            kg_text += f"- Soggetto: {triplet['subject']}, Predicato: {triplet['predicate']}, Oggetto: {triplet['object']} (Fonti: {sources})\n"

        # Costruisci prompt base
        prompt = f"""
        Sei un assistente per l'analisi di Human Digital Twins. Il tuo compito è identificare potenziali trigger di intervento analizzando il knowledge graph e i dati contestuali forniti.
        
        # KNOWLEDGE GRAPH:
        {kg_text}
        """

        # Aggiungi dati profilo se disponibili
        if profile_data:
            profile_text = "\n".join(
                [f"- {key}: {value}" for key, value in profile_data.items()]
            )
            prompt += f"""
            # DATI PROFILO:
            {profile_text}
            """

        # Aggiungi dati fisiologici se disponibili
        if physiological_data:
            physio_text = "\n".join(
                [f"- {metric}: {value}" for metric, value in physiological_data.items()]
            )
            prompt += f"""
            # DATI FISIOLOGICI:
            {physio_text}
            """

        # Aggiungi dati calendario se disponibili
        if calendar_data:
            calendar_text = "\n".join(
                [
                    f"- {event['title']}: {event['start_time']} -> {event['end_time']}"
                    for event in calendar_data
                ]
            )
            prompt += f"""
            # EVENTI CALENDARIO:
            {calendar_text}
            """

        # Aggiungi istruzioni di analisi
        prompt += """
        # COMPITO:
        Analizza questi dati per identificare potenziali trigger di intervento. Un trigger di intervento è una condizione o situazione che richiede un'azione o un supporto.
        
        Per ogni trigger identificato, fornisci:
        1. Tipo di trigger
        2. Punteggio di confidenza (0-1)
        3. Descrizione dettagliata
        4. Evidenze a supporto basate sui dati forniti
        
        Includi anche il tuo processo di ragionamento che spiega come sei arrivato a queste conclusioni.
        """

        return prompt

    @staticmethod
    def intervention_recommendation_prompt(
        triggers: List[Dict[str, Any]], profile_data: Dict[str, Any]
    ) -> str:
        """
        Crea un prompt per generare raccomandazioni di intervento basate sui trigger identificati

        Args:
            triggers: Lista di trigger di intervento identificati
            profile_data: Dati profilo dell'utente

        Returns:
            Prompt formattato
        """
        # Crea rappresentazione testuale dei trigger
        triggers_text = ""
        for i, trigger in enumerate(triggers, 1):
            triggers_text += f"""
            TRIGGER #{i}:
            - Tipo: {trigger['trigger_type']}
            - Confidenza: {trigger['confidence']}
            - Descrizione: {trigger['description']}
            """

        # Crea rappresentazione testuale del profilo
        profile_text = "\n".join(
            [f"- {key}: {value}" for key, value in profile_data.items()]
        )

        # Costruisci prompt
        prompt = f"""
        Sei un assistente per l'analisi di Human Digital Twins. Il tuo compito è generare raccomandazioni di intervento personalizzate basate sui trigger identificati e sul profilo dell'utente.
        
        # TRIGGER IDENTIFICATI:
        {triggers_text}
        
        # PROFILO UTENTE:
        {profile_text}
        
        # COMPITO:
        Genera raccomandazioni di intervento personalizzate per ciascun trigger identificato. Le raccomandazioni dovrebbero essere:
        1. Specifiche e attuabili
        2. Appropriate per il profilo dell'utente
        3. Basate su evidenze
        4. Ordinate per priorità
        
        Per ogni raccomandazione, spiega il ragionamento dietro di essa e come si collega ai dati del profilo utente.
        """

        return prompt
