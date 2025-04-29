import argparse
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

from config.config_loader import ConfigLoader
from data_layer.data_manager import DataManager
from pdb.brain import PersonalDigitalBrain
from llm.provider import get_llm_with_structured_output, reset_model_cache
from models.output_schemas import AnalysisResult


class Simulation:
    """
    Gestisce le simulazioni per valutare l'impatto di informazioni contestuali diverse
    sulla precisione della classificazione degli interventi.
    """

    def __init__(self, data_dir: str, output_dir: str):
        """
        Inizializza la simulazione

        Args:
            data_dir: Directory contenente i dati di simulazione
            output_dir: Directory dove salvare i risultati
        """
        self.config = ConfigLoader()
        self.data_manager = DataManager()
        self.data_dir = data_dir
        self.output_dir = output_dir

        # Crea directory output se non esiste
        os.makedirs(self.output_dir, exist_ok=True)

    def run_simulation(self, scenario_name: str, context_types: List[str]):
        """
        Esegue una simulazione con un determinato scenario e tipi di contesto

        Args:
            scenario_name: Nome dello scenario da simulare
            context_types: Lista di tipi di contesto da includere
                          ('voice', 'profile', 'sensors', 'apps')
        """
        print(
            f"Esecuzione simulazione '{scenario_name}' con contesti: {', '.join(context_types)}"
        )

        # Crea un'istanza pulita di PersonalDigitalBrain per questa simulazione
        brain = PersonalDigitalBrain()

        # Carica dati in base ai tipi di contesto richiesti
        if "voice" in context_types:
            voice_data = self.data_manager.load_voice_data(
                os.path.join(self.data_dir, "voice", f"{scenario_name}.json")
            )
            profile_data = {}
            if "profile" in context_types:
                profile_data = self.data_manager.load_profile_data(
                    os.path.join(self.data_dir, "profiles")
                )
            brain.process_unstructured_data(voice_data, profile_data)

        sensor_data = {}
        app_data = {}
        if "sensors" in context_types:
            sensor_data = self.data_manager.load_sensor_data(
                os.path.join(self.data_dir, "sensors")
            )
        if "apps" in context_types:
            app_data = self.data_manager.load_app_data(
                os.path.join(self.data_dir, "apps")
            )

        if sensor_data or app_data:
            brain.process_structured_data(sensor_data, app_data)

        # Identifica trigger di intervento
        print(f"Analisi del knowledge graph per scenario '{scenario_name}'...")
        result = brain.identify_intervention_triggers()

        # Salva risultati
        self._save_results(scenario_name, context_types, result)

        return result

    def run_batch_simulations(
        self, scenarios: List[str], context_combinations: List[List[str]]
    ):
        """
        Esegue più simulazioni con diverse combinazioni di contesto

        Args:
            scenarios: Lista di nomi scenari da simulare
            context_combinations: Lista di combinazioni di tipi di contesto
        """
        results = {}

        for scenario in scenarios:
            scenario_results = {}
            for contexts in context_combinations:
                # Reimposta la cache del modello tra le simulazioni
                reset_model_cache()

                # Nome della combinazione di contesto
                context_key = "+".join(contexts) if contexts else "baseline"

                # Esegui simulazione
                result = self.run_simulation(scenario, contexts)

                # Salva risultato
                scenario_results[context_key] = {
                    "identified_triggers": [
                        t.dict() for t in result.identified_triggers
                    ],
                    "trigger_count": len(result.identified_triggers),
                }

            results[scenario] = scenario_results

        # Salva risultati aggregati
        self._save_aggregated_results(results)

    def _save_results(
        self, scenario_name: str, context_types: List[str], result: AnalysisResult
    ):
        """
        Salva i risultati di una simulazione

        Args:
            scenario_name: Nome dello scenario
            context_types: Tipi di contesto inclusi
            result: Risultato dell'analisi
        """
        # Crea nome file risultati
        context_str = "_".join(context_types) if context_types else "baseline"
        result_file = os.path.join(
            self.output_dir, f"{scenario_name}_{context_str}_{int(time.time())}.json"
        )

        # Salva risultati
        with open(result_file, "w") as f:
            json.dump(
                {
                    "scenario": scenario_name,
                    "context_types": context_types,
                    "timestamp": datetime.now().isoformat(),
                    "result": result.dict(),
                },
                f,
                indent=2,
            )

        print(f"Risultati salvati in {result_file}")

    def _save_aggregated_results(self, results: Dict[str, Any]):
        """
        Salva risultati aggregati di tutte le simulazioni

        Args:
            results: Risultati aggregati
        """
        result_file = os.path.join(
            self.output_dir, f"aggregated_results_{int(time.time())}.json"
        )

        with open(result_file, "w") as f:
            json.dump(
                {"timestamp": datetime.now().isoformat(), "results": results},
                f,
                indent=2,
            )

        print(f"Risultati aggregati salvati in {result_file}")


def main():
    """
    Punto d'ingresso principale per eseguire simulazioni
    """
    parser = argparse.ArgumentParser(description="Simulazioni Human Digital Twin")
    parser.add_argument(
        "--data-dir", default="data/raw", help="Directory dati simulazione"
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed/results",
        help="Directory per salvare risultati",
    )
    parser.add_argument("--scenario", help="Nome singolo scenario da simulare")
    parser.add_argument(
        "--contexts",
        nargs="+",
        default=["voice", "profile", "sensors", "apps"],
        help="Tipi di contesto da includere (voice, profile, sensors, apps)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Esegui simulazioni batch con diverse combinazioni",
    )
    args = parser.parse_args()

    simulation = Simulation(args.data_dir, args.output_dir)

    if args.batch:
        # Esegui simulazioni batch con diverse combinazioni di contesto
        scenarios = ["episode1_conversation"]  # Aggiungi qui altri scenari

        # Definisci combinazioni di contesto da testare
        context_combinations = [
            [],  # Baseline (nessun contesto)
            ["voice"],  # Solo voce
            ["voice", "profile"],  # Voce + profilo
            ["voice", "sensors"],  # Voce + sensori
            ["voice", "profile", "sensors"],  # Voce + profilo + sensori
            ["voice", "profile", "sensors", "apps"],  # Tutti i contesti
        ]

        simulation.run_batch_simulations(scenarios, context_combinations)
    else:
        # Esegui singola simulazione
        scenario = args.scenario or "episode1_conversation"
        simulation.run_simulation(scenario, args.contexts)


if __name__ == "__main__":
    main()
