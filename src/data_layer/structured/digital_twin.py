import os
import json
import csv
from typing import Dict, Any, List


class DigitalTwin:
    """
    Rappresenta Digital Twins per dispositivi IoT e gestisce dati sensori
    """

    def load_sensor_data(self, file_path: str) -> Dict[str, Any]:
        """
        Carica dati sensori da file

        Args:
            file_path: Percorso ai file dati sensori

        Returns:
            Dati sensori elaborati
        """
        sensor_data = {}

        # Controlla se il percorso è una directory o un file
        if os.path.isdir(file_path):
            # Elabora tutti i file dati sensori nella directory
            for filename in os.listdir(file_path):
                file_full_path = os.path.join(file_path, filename)
                if os.path.isfile(file_full_path):
                    # Estrai ID dispositivo dal nome file
                    device_id = os.path.splitext(filename)[0]
                    sensor_data[device_id] = self._load_sensor_file(file_full_path)
        else:
            # File singolo - usa il nome file come ID dispositivo
            device_id = os.path.splitext(os.path.basename(file_path))[0]
            sensor_data[device_id] = self._load_sensor_file(file_path)

        return sensor_data

    def _load_sensor_file(self, file_path: str) -> Dict[str, Dict[str, float]]:
        """
        Carica un singolo file dati sensori

        Args:
            file_path: Percorso al file dati sensori

        Returns:
            Letture sensori dal file
        """
        readings = {}

        if file_path.endswith(".json"):
            # Carica formato JSON
            with open(file_path, "r") as f:
                data = json.load(f)

            # Elabora dati JSON in base al formato previsto
            if isinstance(data, dict):
                for reading_type, values in data.items():
                    if isinstance(values, dict):
                        readings[reading_type] = values
                    elif isinstance(values, list) and all(
                        isinstance(item, dict) for item in values
                    ):
                        # Lista di letture con timestamp e valore
                        readings[reading_type] = {
                            item.get("timestamp", f"reading_{i}"): item.get("value")
                            for i, item in enumerate(values)
                            if "value" in item
                        }

        elif file_path.endswith(".csv"):
            # Carica formato CSV
            with open(file_path, "r") as f:
                csv_reader = csv.DictReader(f)

                # Prima, raccogli tutte le righe
                rows = list(csv_reader)

                # Controlla se CSV è organizzato per tipo lettura o per timestamp
                if (
                    "timestamp" in csv_reader.fieldnames
                    and len(csv_reader.fieldnames) > 2
                ):
                    # CSV organizzato con timestamp nella prima colonna e tipi lettura nelle altre colonne
                    for reading_type in [
                        f for f in csv_reader.fieldnames if f != "timestamp"
                    ]:
                        readings[reading_type] = {}
                        for row in rows:
                            if row["timestamp"] and row[reading_type]:
                                readings[reading_type][row["timestamp"]] = float(
                                    row[reading_type]
                                )
                else:
                    # Assume CSV con colonne reading_type, timestamp, value
                    for row in rows:
                        reading_type = row.get("reading_type", "")
                        timestamp = row.get("timestamp", "")
                        value = row.get("value", "")

                        if reading_type and timestamp and value:
                            if reading_type not in readings:
                                readings[reading_type] = {}
                            readings[reading_type][timestamp] = float(value)

        return readings
