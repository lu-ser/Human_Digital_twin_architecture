from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Triple(BaseModel):
    """Rappresenta un triplet di conoscenza (soggetto, predicato, oggetto)"""
    subject: str = Field(..., description="Entità soggetto del triplet")
    predicate: str = Field(..., description="Relazione o predicato del triplet")
    object: str = Field(..., description="Entità oggetto del triplet")

class InterventionTrigger(BaseModel):
    """Rappresenta un trigger di intervento identificato"""
    trigger_type: str = Field(..., description="Tipo di trigger di intervento identificato")
    confidence: float = Field(..., description="Punteggio di confidenza per questo trigger (0-1)")
    description: str = Field(..., description="Descrizione dettagliata del trigger")
    supporting_evidence: Dict[str, Any] = Field(..., description="Evidenze a supporto dell'identificazione di questo trigger")
    
class AnalysisResult(BaseModel):
    """Rappresenta il risultato completo dell'analisi LLM"""
    extracted_triples: List[Triple] = Field(..., description="Triplet estratti dai dati di input")
    identified_triggers: List[InterventionTrigger] = Field(..., description="Trigger di intervento identificati")
    reasoning: str = Field(..., description="Processo di ragionamento che ha portato a queste conclusioni")