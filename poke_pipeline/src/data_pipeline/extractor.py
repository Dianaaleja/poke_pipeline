import requests
from typing import List, Dict, Any

# Define the base URL for the PokeAPI
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

def fetch_pokemon_details(pokemon_url: str) -> Dict[str, Any] | None:
    """
    Fetches the detailed JSON data for a single Pokémon using its URL.

    Args:
        pokemon_url: The specific URL for the Pokémon's detail endpoint.

    Returns:
        The detailed Pokémon data as a dictionary, or None if the request fails.
    """
    try:
        response = requests.get(pokemon_url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch detail from {pokemon_url}. Exception: {e}")
        return None

def extract_raw_data(limit: int = 20) -> List[Dict[str, Any]]:
    """
    The main extraction function. It orchestrates two steps:
    1. Fetches a list of Pokémon endpoints.
    2. Fetches the detailed data for each Pokémon in the list.

    Args:
        limit: The maximum number of Pokémon details to fetch. Defaults to 20.

    Returns:
        A list of dictionaries containing the raw JSON data for all successfully fetched Pokémon.
    """
    print(f"--- Starting Data Extraction for {limit} Pokémon ---")
    pokemon_urls: List[str] = []
    
    # 1. Fetch the list of Pokémon URLs
    try:
        # Use offset 0 and the provided limit to get the first N Pokémon
        list_url = f"{POKEAPI_BASE_URL}?limit={limit}&offset=0"
        list_response = requests.get(list_url, timeout=10)
        list_response.raise_for_status()
        list_data = list_response.json()
        
        # Extract the detail URL for each Pokémon
        for item in list_data.get("results", []):
            pokemon_urls.append(item["url"])
        
        print(f"Successfully retrieved {len(pokemon_urls)} Pokémon endpoints.")
        
    except requests.exceptions.RequestException as e:
        print(f"FATAL ERROR: Failed to retrieve the initial Pokémon list. Exception: {e}")
        return []

    # 2. Fetch details for each Pokémon
    raw_data_list: List[Dict[str, Any]] = []
    
    for url in pokemon_urls:
        detail_data = fetch_pokemon_details(url)
        if detail_data:
            raw_data_list.append(detail_data)
            
    print(f"--- Extraction Complete. {len(raw_data_list)} Pokémon data points successfully collected. ---")
    return raw_data_list

# --- Example Usage (for local testing) ---
if __name__ == '__main__':
    # Ensure you have 'requests' installed: pip install requests
    test_data = extract_raw_data(limit=3)
    
    if test_data:
        print(f"\nExample of extracted data (first item):\n{test_data[0]['name']}")
        print(f"Number of types: {len(test_data[0]['types'])}")
    else:
        print("\nNo data was extracted successfully.")