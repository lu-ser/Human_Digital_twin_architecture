import os
import json
from typing import List, Dict, Any

class VoiceProcessor:
    """
    Gestisce il caricamento e il preprocessing dei dati di trascrizione vocale
    """
    
    def load_and_process(self, file_path: str) -> str:
        """
        Carica e pre-elabora dati di trascrizione vocale
        
        Args:
            file_path: Percorso al file dati vocali o directory
            
        Returns:
            Testo vocale elaborato
        """
        # Controlla se il percorso è una directory o un file
        if os.path.isdir(file_path):
            # Carica tutti i file di trascrizione nella directory
            transcripts = []
            for filename in sorted(os.listdir(file_path)):
                if filename.endswith('.json') or filename.endswith('.txt'):
                    file_full_path = os.path.join(file_path, filename)
                    transcripts.append(self._load_transcript_file(file_full_path))
            
            # Combina tutte le trascrizioni
            return "\n\n".join(transcripts)
        else:
            # Carica un singolo file di trascrizione
            return self._load_transcript_file(file_path)
    
    def _load_transcript_file(self, file_path: str) -> str:
        """
        Carica un singolo file di trascrizione
        
        Args:
            file_path: Percorso al file
            
        Returns:
            Contenuto testuale del file
        """
        if file_path.endswith('.json'):
            # Carica formato JSON
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Controlla formato previsto
            if isinstance(data, list):
                # Lista di espressioni
                if all(isinstance(item, str) for item in data):
                    return "\n".join(data)
                # Lista di oggetti con campo text
                elif all(isinstance(item, dict) and 'text' in item for item in data):
                    return "\n".join(item['text'] for item in data)
            elif isinstance(data, dict) and 'transcript' in data:
                # Oggetto con campo transcript
                return data['transcript']
            
            # Fallback: converti in stringa
            return str(data)
        else:
            # Carica formato testo
            with open(file_path, 'r') as f:
                return f.read()