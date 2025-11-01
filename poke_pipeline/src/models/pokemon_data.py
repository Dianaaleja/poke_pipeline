from pydantic import BaseModel
from typing import List, Optional

# This file defines the expected structure of the CLEAN/TRANSFORMED data
# that is ready to be loaded into the SQL database.
# Using Pydantic adds data validation and clarity.

class TypeModel(BaseModel):
    """Corresponds to the 'type' SQL table."""
    id: int
    name: str

class PokemonTypeModel(BaseModel):
    """Corresponds to the 'pokemon_type' junction SQL table."""
    pokemon_id: int
    type_id: int
    slot: int

class PokemonModel(BaseModel):
    """Corresponds to the 'pokemon' SQL table."""
    id: int
    name: str
    height: Optional[float] 
    weight: Optional[float]
    base_experience: Optional[int]

# You would then update transformer.py to return lists of these Pydantic objects 
# instead of raw dictionaries, adding a layer of validation.