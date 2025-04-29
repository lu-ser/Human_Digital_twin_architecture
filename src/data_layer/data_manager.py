from config.config_loader import ConfigLoader
from data_layer.unstructured.voice_processor import VoiceProcessor
from data_layer.unstructured.profile_processor import ProfileProcessor
from data_layer.structured.digital_twin import DigitalTwin
from data_layer.structured.app_data import AppDataProcessor
from typing import Dict, Any


class DataManager:
    """
    Gestisce l'acquisizione e il preprocessing dei dati da diverse fonti
    """

    def __init__(self):
        self.config = ConfigLoader()
        self.voice_processor = VoiceProcessor()
        self.profile_processor = ProfileProcessor()
        self.digital_twin = DigitalTwin()
        self.app_data_processor = AppDataProcessor()

    def load_voice_data(self, file_path: str = None) -> str:
        """
        Carica e pre-elabora dati di trascrizione vocale

        Args:
            file_path: Percorso opzionale al file dati vocali

        Returns:
            Testo vocale elaborato
        """
        if file_path is None:
            file_path = self.config.get_value("data_sources.voice.path")

        return self.voice_processor.load_and_process(file_path)

    def load_profile_data(self, file_path: str = None) -> Dict[str, Any]:
        """
        Carica dati profilo utente

        Args:
            file_path: Percorso opzionale al file dati profilo

        Returns:
            Dati profilo utente
        """
        if file_path is None:
            file_path = self.config.get_value("data_sources.profile.path")

        return self.profile_processor.load_profile(file_path)

    def load_sensor_data(self, file_path: str = None) -> Dict[str, Any]:
        """
        Carica dati sensori dai Digital Twins

        Args:
            file_path: Percorso opzionale al file dati sensori

        Returns:
            Dati sensori
        """
        if file_path is None:
            file_path = self.config.get_value("data_sources.sensors.path")

        return self.digital_twin.load_sensor_data(file_path)

    def load_app_data(self, file_path: str = None) -> Dict[str, Any]:
        """
        Carica dati applicazioni

        Args:
            file_path: Percorso opzionale al file dati app

        Returns:
            Dati applicazioni
        """
        if file_path is None:
            file_path = self.config.get_value("data_sources.apps.path")

        return self.app_data_processor.load_app_data(file_path)
