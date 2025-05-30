from config.config_loader import ConfigLoader
from llm.provider import get_llm_with_structured_output
from models.output_schemas import Triple, TripletList
from typing import List, Dict, Any


class TripletExtractor:
    """
    Extracts knowledge triplets from unstructured text using LLM
    """

    def __init__(self):
        self.config = ConfigLoader()

    def extract_from_text(self, text: str) -> List[Dict[str, str]]:
        """
        Extracts triplets from unstructured text

        Args:
            text: Input text to process

        Returns:
            List of extracted triplets
        """
        # Get LLM with structured output using TripletList model
        llm = get_llm_with_structured_output(TripletList)

        # Create the message with explicit JSON formatting instructions
        message = f"""
        You are a knowledge triplet extraction system. Your task is to extract subject-predicate-object triplets from the provided text.

        Guidelines:
        - Focus on extracting factual information
        - Identify entities (people, objects, concepts) as subjects and objects
        - Identify relationships between entities as predicates
        - Extract only explicit information, do not infer

        Extract knowledge triplets from the following text:

        {text}
        """

        # Extract triplets using structured output
        result = llm.invoke(message)

        # Convert to dictionary format
        return [triplet.dict() for triplet in result.triplets]

    def extract_from_profile(
        self, profile_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Extract triplets from profile information

        Args:
            profile_data: User profile data

        Returns:
            List of extracted triplets
        """
        # Convert profile data to text format
        profile_text = self._profile_to_text(profile_data)

        # Use the same text extraction method
        return self.extract_from_text(profile_text)

    def _profile_to_text(self, profile_data: Dict[str, Any]) -> str:
        """
        Convert profile data to text format for processing

        Args:
            profile_data: User profile data

        Returns:
            Text representation of the profile
        """
        # Simple conversion of profile dictionary to text
        profile_text = "User Profile:\n"

        for key, value in profile_data.items():
            if isinstance(value, dict):
                profile_text += f"{key}:\n"
                for sub_key, sub_value in value.items():
                    profile_text += f"  {sub_key}: {sub_value}\n"
            else:
                profile_text += f"{key}: {value}\n"

        return profile_text
