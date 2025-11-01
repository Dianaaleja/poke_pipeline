import json
from typing import Dict, List, Any, Tuple
from models.pokemon_data import PokemonModel, TypeModel, PokemonTypeModel # <-- NEW IMPORT

# --- Global State for Type Mapping (Crucial for Normalization) ---
_type_name_to_id: Dict[str, int] = {}
_next_type_id: int = 1

def transform_pokemon_data(
    raw_data_list: List[Dict[str, Any]]
) -> Tuple[List[PokemonModel], List[TypeModel], List[PokemonTypeModel]]:
    """
    Transforms a list of raw JSON responses from the PokeAPI into three
    structured Pydantic model lists suitable for loading into the SQL database tables:
    'pokemon', 'type', and 'pokemon_type'.

    The Pydantic models ensure type validation and structural integrity.

    Args:
        raw_data_list: A list of raw JSON dictionaries from the API.

    Returns:
        A tuple containing three lists of Pydantic model objects, in this order:
        (pokemon_models, type_models, pokemon_type_models)
    """
    
    # Reset global state for the type mapping upon a new run
    global _type_name_to_id
    global _next_type_id
    _type_name_to_id = {}
    _next_type_id = 1
    
    pokemon_records: List[Dict[str, Any]] = []
    pokemon_type_records: List[Dict[str, Any]] = []
    
    for data in raw_data_list:
        # 1. Dictionary preparation for the 'pokemon' table
        pokemon_dict = {
            "id": data.get("id"),
            "name": data.get("name"),
            "height": data.get("height"),
            "weight": data.get("weight"),
            "base_experience": data.get("base_experience")
        }
        pokemon_records.append(pokemon_dict)

        # 2. Transformation for the 'type' and 'pokemon_type' tables
        types_list = data.get("types", [])
        
        for type_entry in types_list:
            type_name = type_entry["type"]["name"]
            slot = type_entry["slot"]
            
            # --- Type Normalization Logic ---
            if type_name not in _type_name_to_id:
                _type_name_to_id[type_name] = _next_type_id
                _next_type_id += 1
            
            type_id = _type_name_to_id[type_name]
            
            # 3. Build the dictionary for the 'pokemon_type' junction table
            pokemon_type_dict = {
                "pokemon_id": pokemon_dict["id"],
                "type_id": type_id,
                "slot": slot
            }
            pokemon_type_records.append(pokemon_type_dict)

    # 4. Final list of dictionaries for the 'type' table
    type_records = [
        {"id": type_id, "name": type_name}
        for type_name, type_id in _type_name_to_id.items()
    ]
    
    # --- Pydantic Validation and Conversion (The NEW Step!) ---
    # Convert the raw dictionaries into validated Pydantic models
    
    # Validate Type Models
    type_models = [TypeModel(**r) for r in type_records]
    
    # Validate Pokemon Models
    pokemon_models = [PokemonModel(**r) for r in pokemon_records]
    
    # Validate PokemonType Models
    pokemon_type_models = [PokemonTypeModel(**r) for r in pokemon_type_records]


    return pokemon_models, type_models, pokemon_type_models

# --- Example Usage (for local testing) ---
# (Omitted for brevity, but the logic remains the same, just returning models)
