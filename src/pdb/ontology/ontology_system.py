from typing import Dict, List, Any

class OntologySystem:
    """
    Gestisce l'integrazione di ontologie e mappatura semantica per il sistema HDT.
    Converte dati strutturati in triplet compatibili con il knowledge graph.
    """
    
    def __init__(self):
        # In un'implementazione reale, questo caricherebbe e integrerebbe le ontologie
        # Per ora, usiamo un approccio semplificato
        pass
    
    def sensor_data_to_triplets(self, sensor_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Converte dati dei sensori in triplet di conoscenza
        
        Args:
            sensor_data: Dati dai sensori/dispositivi IoT
            
        Returns:
            Lista di triplet di conoscenza
        """
        triplets = []
        
        # Elabora ogni lettura del sensore
        for device_id, readings in sensor_data.items():
            # Aggiungi informazioni sul dispositivo
            triplets.append({
                "subject": f"device:{device_id}",
                "predicate": "rdf:type",
                "object": "sosa:Sensor"
            })
            
            # Elabora letture
            for reading_type, values in readings.items():
                for timestamp, value in values.items():
                    # Crea un ID unico per questa osservazione
                    observation_id = f"observation:{device_id}_{reading_type}_{timestamp}"
                    
                    # Aggiungi informazioni sull'osservazione
                    triplets.append({
                        "subject": observation_id,
                        "predicate": "rdf:type", 
                        "object": "sosa:Observation"
                    })
                    
                    triplets.append({
                        "subject": observation_id,
                        "predicate": "sosa:madeBySensor",
                        "object": f"device:{device_id}"
                    })
                    
                    triplets.append({
                        "subject": observation_id,
                        "predicate": "sosa:observedProperty",
                        "object": f"property:{reading_type}"
                    })
                    
                    triplets.append({
                        "subject": observation_id,
                        "predicate": "sosa:hasSimpleResult",
                        "object": str(value)
                    })
                    
                    triplets.append({
                        "subject": observation_id,
                        "predicate": "sosa:resultTime",
                        "object": timestamp
                    })
        
        return triplets
    
    def app_data_to_triplets(self, app_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Converte dati delle applicazioni in triplet di conoscenza
        
        Args:
            app_data: Dati dalle applicazioni
            
        Returns:
            Lista di triplet di conoscenza
        """
        triplets = []
        
        # Elabora i dati di ogni app
        for app_id, entries in app_data.items():
            # Aggiungi informazioni sull'app
            triplets.append({
                "subject": f"app:{app_id}",
                "predicate": "rdf:type",
                "object": "schema:SoftwareApplication"
            })
            
            # Elabora le entries
            for entry_id, entry_data in entries.items():
                # Crea un ID unico per questa entry
                item_id = f"entry:{app_id}_{entry_id}"
                
                # Aggiungi informazioni sull'entry
                triplets.append({
                    "subject": item_id,
                    "predicate": "schema:sourceApplication",
                    "object": f"app:{app_id}"
                })
                
                # Elabora ogni campo nell'entry
                for key, value in entry_data.items():
                    if key == "timestamp":
                        triplets.append({
                            "subject": item_id,
                            "predicate": "schema:dateCreated",
                            "object": value
                        })
                    else:
                        # Usa la chiave come predicato, con namespace appropriato
                        triplets.append({
                            "subject": item_id,
                            "predicate": f"schema:{key}",
                            "object": str(value)
                        })
        
        return triplets