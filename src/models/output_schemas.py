from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Triple(BaseModel):
    """Represents a knowledge triplet (subject, predicate, object)"""

    subject: str = Field(..., description="Subject entity of the triplet")
    predicate: str = Field(..., description="Relation or predicate of the triplet")
    object: str = Field(..., description="Object entity of the triplet")


class TripletList(BaseModel):
    """Represents a list of knowledge triplets"""

    triplets: List[Triple] = Field(..., description="List of extracted triplets")


class InterventionTrigger(BaseModel):
    """Represents an identified intervention trigger"""

    trigger_type: str = Field(
        ..., description="Type of identified intervention trigger"
    )
    confidence: float = Field(
        ..., description="Confidence score for this trigger (0-1)"
    )
    description: str = Field(..., description="Detailed description of the trigger")
    supporting_evidence: Dict[str, Any] = Field(
        ..., description="Evidence supporting the identification of this trigger"
    )


class AnalysisResult(BaseModel):
    """Represents the complete LLM analysis result"""

    extracted_triples: List[Triple] = Field(
        ..., description="Triplets extracted from input data"
    )
    identified_triggers: List[InterventionTrigger] = Field(
        ..., description="Identified intervention triggers"
    )
    reasoning: str = Field(
        ..., description="Reasoning process that led to these conclusions"
    )
