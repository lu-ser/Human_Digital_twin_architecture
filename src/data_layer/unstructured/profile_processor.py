import os
import json
import yaml
from typing import Dict, Any

class ProfileProcessor:
    """
    Gestisce il caricamento e l'elaborazione dei dati del profilo utente
    """
    
    def load_profile(self, file_path: str) -> Dict[str, Any]:
        """
        Carica dati profilo utente
        
        Args:
            file_path: Percorso al file dati profilo o directory
            
        Returns:
            Dati profilo utente
        """
        # Controlla se il percorso è una directory o un file
        if os.path.isdir(file_path):
            # Carica profile.json o profile.yaml se esistono
            for filename in ['profile.json', 'profile.yaml', 'profile.yml']:
                full_path = os.path.join(file_path, filename)
                if os.path.exists(full_path):
                    return self._load_profile_file(full_path)
            
            # Se non c'è un file profilo principale, unisci tutti i file profilo
            profile_data = {}
            for filename in sorted(os.listdir(file_path)):
                if filename.endswith('.json') or filename.endswith('.yaml') or filename.endswith('.yml'):
                    file_full_path = os.path.join(file_path, filename)
                    file_data = self._load_profile_file(file_full_path)
                    
                    # Unisci con i dati esistenti
                    profile_data.update(file_data)
            
            return profile_data
        else:
            # Carica singolo file profilo
            return self._load_profile_file(file_path)
    
    def _load_profile_file(self, file_path: str) -> Dict[str, Any]:
        """
        Carica un singolo file profilo
        
        Args:
            file_path: Percorso al file
            
        Returns:
            Dati profilo dal file
        """
        if file_path.endswith('.json'):
            # Carica formato JSON
            with open(file_path, 'r') as f:
                return json.load(f)
        elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
            # Carica formato YAML
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Formato non supportato
            raise ValueError(f"Formato file profilo non supportato: {file_path}")