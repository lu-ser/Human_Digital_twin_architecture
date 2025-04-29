from config.config_loader import ConfigLoader
from llm.provider import get_llm_with_structured_output
from models.output_schemas import AnalysisResult
from pdb.triplet_extraction.extractor import TripletExtractor
from pdb.ontology.ontology_system import OntologySystem
from typing import Dict, List, Any


class PersonalDigitalBrain:
    """
    Componente centrale del sistema HDT che integra ed elabora dati
    da varie fonti per creare una rappresentazione completa dell'utente.
    """

    def __init__(self):
        self.config = ConfigLoader()
        self.triplet_extractor = TripletExtractor()
        self.ontology_system = OntologySystem()
        self.knowledge_graph = {}  # Rappresentazione semplificata del knowledge graph

    def process_unstructured_data(self, voice_data: str, profile_data: Dict[str, Any]):
        """
        Elabora dati non strutturati (voce e profilo)

        Args:
            voice_data: Testo dalla trascrizione vocale
            profile_data: Informazioni profilo utente
        """
        # Estrai triplet dai dati vocali
        voice_triplets = self.triplet_extractor.extract_from_text(voice_data)

        # Aggiungi triplet al knowledge graph
        self._add_triplets_to_graph(voice_triplets, "voice")

        # Elabora dati del profilo
        profile_triplets = self.triplet_extractor.extract_from_profile(profile_data)
        self._add_triplets_to_graph(profile_triplets, "profile")

    def process_structured_data(
        self, sensor_data: Dict[str, Any], app_data: Dict[str, Any]
    ):
        """
        Elabora dati strutturati (sensori e app)

        Args:
            sensor_data: Dati da sensori/dispositivi IoT
            app_data: Dati da applicazioni
        """
        # Elabora dati sensori
        sensor_triplets = self.ontology_system.sensor_data_to_triplets(sensor_data)
        self._add_triplets_to_graph(sensor_triplets, "sensor")

        # Elabora dati app
        app_triplets = self.ontology_system.app_data_to_triplets(app_data)
        self._add_triplets_to_graph(app_triplets, "app")

    def identify_intervention_triggers(self) -> AnalysisResult:
        """
        Analizza il knowledge graph per identificare potenziali trigger di intervento

        Returns:
            Risultato analisi con trigger identificati
        """
        # Crea un prompt basato sul knowledge graph
        prompt = self._create_analysis_prompt()

        # Usa LLM per analizzare il knowledge graph
        llm = get_llm_with_structured_output(AnalysisResult)
        result = llm.invoke(prompt)

        return result

    def _add_triplets_to_graph(self, triplets: List[Dict[str, str]], source: str):
        """
        Aggiungi triplet estratti al knowledge graph

        Args:
            triplets: Lista di triplet da aggiungere
            source: Fonte dei triplet (voice, profile, sensor, app)
        """
        # Implementazione semplificata - in un sistema reale, questo userebbe un database a grafo
        for triplet in triplets:
            # Crea un identificatore unico per il triplet
            triplet_id = (
                f"{triplet['subject']}_{triplet['predicate']}_{triplet['object']}"
            )

            # Aggiungi al knowledge graph con informazioni sulla fonte
            if triplet_id not in self.knowledge_graph:
                self.knowledge_graph[triplet_id] = {
                    "triplet": triplet,
                    "sources": [source],
                }
            else:
                # Se il triplet esiste già, aggiungi la nuova fonte
                if source not in self.knowledge_graph[triplet_id]["sources"]:
                    self.knowledge_graph[triplet_id]["sources"].append(source)

    def _create_analysis_prompt(self) -> str:
        """
        Crea un prompt per il LLM che spiega come interrogare il knowledge graph

        Returns:
            Stringa prompt formattata
        """
        # Creazione di metadati del knowledge graph
        sources = set()
        predicates = set()
        entity_types = set()

        for triplet_id, data in self.knowledge_graph.items():
            triplet = data["triplet"]
            sources.update(data["sources"])
            predicates.add(triplet["predicate"])

            # Estrazione informazioni sui tipi se disponibili
            if triplet["predicate"] == "rdf:type":
                entity_types.add(triplet["object"])

        # Rappresentazione testuale dei metadati
        metadata = f"""
        Fonti dati: {', '.join(sources)}
        Tipi di relazioni: {', '.join(predicates)}
        Tipi di entità: {', '.join(entity_types)}
        """

        # Prompt principale
        prompt = f"""
        Stai analizzando un knowledge graph di un Human Digital Twin per identificare potenziali trigger di intervento.
        
        Il knowledge graph contiene i seguenti tipi di informazioni:
        {metadata}
        
        Invece di fornirti l'intero knowledge graph, puoi interrogarlo usando query SPARQL-like. Ad esempio:
        
        QUERY: SELECT ?subject ?predicate ?object WHERE {{ ?subject ?predicate ?object . FILTER(?predicate = "sosa:hasSimpleResult") }}
        
        Questa query restituirebbe tutti i triplet dove il predicato è "sosa:hasSimpleResult".
        
        Il tuo compito è:
        
        1. Formulare query per recuperare parti rilevanti del knowledge graph
        2. Analizzare i risultati per identificare pattern o anomalie che potrebbero indicare la necessità di un intervento
        3. Per ogni trigger di intervento che identifichi, fornisci:
        a. Il tipo di trigger
        b. Un punteggio di confidenza (0-1)
        c. Una descrizione dettagliata
        d. Evidenze a supporto dal knowledge graph
        
        Inizia formulando alcune query iniziali per comprendere cosa è disponibile nel knowledge graph.
        """

        return prompt

    def query_knowledge_graph(self, query_str: str) -> List[Dict[str, str]]:
        """
        Esegue una query sul knowledge graph

        Args:
            query_str: Stringa di query in formato SPARQL-like

        Returns:
            Lista di triplet corrispondenti
        """
        # Implementazione semplificata di parsing query
        filters = {}

        # Parsing base per scopo dimostrativo
        if "FILTER" in query_str:
            filter_parts = query_str.split("FILTER")[1].strip("(){} ").split(" AND ")
            for part in filter_parts:
                if "=" in part:
                    field, value = part.split("=")
                    field = field.strip("? ")
                    value = value.strip(" \"'")
                    filters[field] = value

        # Applicazione filtri al knowledge graph
        results = []
        for triplet_id, data in self.knowledge_graph.items():
            triplet = data["triplet"]

            # Verifica se il triplet corrisponde a tutti i filtri
            match = True
            for field, value in filters.items():
                if field in triplet and triplet[field] != value:
                    match = False
                    break

            if match:
                results.append(triplet)

        return results
