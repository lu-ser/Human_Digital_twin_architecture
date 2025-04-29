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
        Crea un prompt per il LLM per analizzare il knowledge graph

        Returns:
            Stringa prompt formattata
        """
        # Converti knowledge graph in una rappresentazione testuale
        kg_representation = ""
        for triplet_id, data in self.knowledge_graph.items():
            triplet = data["triplet"]
            sources = ", ".join(data["sources"])
            kg_representation += f"- Soggetto: {triplet['subject']}, Predicato: {triplet['predicate']}, Oggetto: {triplet['object']} (Fonti: {sources})\n"

        # Crea il prompt
        prompt = f"""
        Stai analizzando un knowledge graph di un Human Digital Twin per identificare potenziali trigger di intervento.
        
        KNOWLEDGE GRAPH:
        {kg_representation}
        
        Basandoti su questo knowledge graph, identifica eventuali pattern o anomalie che potrebbero indicare la necessità di un intervento.
        Per ogni trigger di intervento che identifichi, fornisci:
        1. Il tipo di trigger
        2. Un punteggio di confidenza (0-1)
        3. Una descrizione dettagliata
        4. Evidenze a supporto dal knowledge graph
        
        Fornisci anche il tuo processo di ragionamento.
        """

        return prompt
