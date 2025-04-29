import argparse
import json
import os
from config.config_loader import ConfigLoader
from data_layer.data_manager import DataManager
from pdb.brain import PersonalDigitalBrain


def main():
    """
    Script principale per eseguire il sistema Human Digital Twin
    """
    parser = argparse.ArgumentParser(description="Sistema Human Digital Twin")
    parser.add_argument("--voice", help="Percorso ai dati vocali")
    parser.add_argument("--profile", help="Percorso ai dati profilo")
    parser.add_argument("--sensors", help="Percorso ai dati sensori")
    parser.add_argument("--apps", help="Percorso ai dati applicazioni")
    parser.add_argument("--output", help="Percorso per salvare risultati")
    args = parser.parse_args()

    config = ConfigLoader()
    data_manager = DataManager()
    brain = PersonalDigitalBrain()

    print("Inizializzazione del sistema Human Digital Twin...")

    # Carica dati da diverse fonti
    print("Caricamento dati non strutturati...")
    voice_data = data_manager.load_voice_data(args.voice)
    profile_data = data_manager.load_profile_data(args.profile)

    print("Caricamento dati strutturati...")
    sensor_data = data_manager.load_sensor_data(args.sensors)
    app_data = data_manager.load_app_data(args.apps)

    # Elabora dati nel Personal Digital Brain
    print("Elaborazione dati non strutturati nel Personal Digital Brain...")
    brain.process_unstructured_data(voice_data, profile_data)

    print("Elaborazione dati strutturati nel Personal Digital Brain...")
    brain.process_structured_data(sensor_data, app_data)

    # Identifica trigger di intervento
    print(
        "Analisi del knowledge graph per identificare potenziali trigger di intervento..."
    )
    results = brain.identify_intervention_triggers()

    # Stampa risultati
    print("\n=== Trigger di Intervento Identificati ===")
    for i, trigger in enumerate(results.identified_triggers, 1):
        print(f"Trigger #{i}:")
        print(f"Tipo: {trigger.trigger_type}")
        print(f"Confidenza: {trigger.confidence}")
        print(f"Descrizione: {trigger.description}")
        print("Evidenze a supporto:")
        for key, value in trigger.supporting_evidence.items():
            print(f"  {key}: {value}")
        print()

    # Salva risultati se è fornito un percorso di output
    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(results.dict(), f, indent=2)
        print(f"Risultati salvati in {args.output}")


if __name__ == "__main__":
    main()
