import os
import json
import yaml
from typing import Dict, Any

class AppDataProcessor:
    """
    Gestisce il caricamento e l'elaborazione dei dati delle applicazioni
    """
    
    def load_app_data(self, file_path: str) -> Dict[str, Any]:
        """
        Carica dati applicazioni
        
        Args:
            file_path: Percorso al file dati app o directory
            
        Returns:
            Dati applicazioni
        """
        app_data = {}
        
        # Controlla se il percorso è una directory o un file
        if os.path.isdir(file_path):
            # Elabora ogni directory/file app
            for app_name in os.listdir(file_path):
                app_path = os.path.join(file_path, app_name)
                
                if os.path.isdir(app_path):
                    # Directory per app specifica - elabora tutti i file all'interno
                    app_entries = {}
                    for filename in os.listdir(app_path):
                        if os.path.isfile(os.path.join(app_path, filename)):
                            entry_id = os.path.splitext(filename)[0]
                            entry_data = self._load_app_file(os.path.join(app_path, filename))
                            app_entries[entry_id] = entry_data
                    
                    app_data[app_name] = app_entries
                elif os.path.isfile(app_path):
                    # File singolo per dati app
                    app_id = os.path.splitext(app_name)[0]
                    app_data[app_id] = self._load_app_file(app_path)
        else:
            # File singolo con tutti i dati app
            all_data = self._load_app_file(file_path)
            
            # Controlla se il file contiene dati organizzati per app
            if isinstance(all_data, dict):
                app_data = all_data
        
        return app_data
    
    def _load_app_file(self, file_path: str) -> Dict[str, Any]:
        """
        Carica un singolo file dati app
        
        Args:
            file_path: Percorso al file
            
        Returns:
            Dati app dal file
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
            raise ValueError(f"Formato file dati app non supportato: {file_path}")