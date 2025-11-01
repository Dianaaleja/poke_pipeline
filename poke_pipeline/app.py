import sys
import os

# --- IMPORTANT NOTE ---
# Given the folder structure, the best practice is to run this script
# from the root folder ('POKE_PIPELINE') using: python app.py
# and use import paths based on the 'src' subdirectory name.

# The following block ensures Python can find 'src' if the script is not executed
# from the root directory. We keep it as a robust safeguard:
# Add the absolute 'src' path at the front of sys.path so imports resolve for both runtime and static analyzers.
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import the core functions using the full package path.
# Try the normal package import first; if that fails (IDE/static analyzer differences), try a fallback import.
try:
    from data_pipeline.extractor import extract_raw_data
    from data_pipeline.transformer import transform_pokemon_data
    from data_pipeline.loader import load_data
except ImportError:
    try:
        # Some environments treat 'src' as part of the import path; try importing via 'src.data_pipeline'.
        from src.data_pipeline.extractor import extract_raw_data  # type: ignore
        from src.data_pipeline.transformer import transform_pokemon_data  # type: ignore
        from src.data_pipeline.loader import load_data  # type: ignore
    except Exception as e:
        raise ImportError("Unable to import 'data_pipeline' modules; ensure the 'src' folder contains the package and sys.path is configured correctly.") from e

# --- Configuration ---
# Define the quantity of Pokémon to load here
POKEMON_LIMIT = 20

def run_pokepipeline():
    """
    Executes the full ETL (Extract, Transform, Load) pipeline.
    
    Orchestration sequence:
    1. Extract data from the PokeAPI.
    2. Transform raw JSON into structured Pydantic models.
    3. Load structured data into the SQLite database.
    """
    print("\n=============================================")
    print("🚀 Starting PokéPipeline ETL Process")
    print("=============================================")

    # 1. EXTRACT: Fetch raw data from PokeAPI
    try:
        raw_data = extract_raw_data(limit=POKEMON_LIMIT)
        if not raw_data:
            print("❌ Pipeline failed: No raw data extracted. Exiting.")
            return
    except Exception as e:
        print(f"❌ Extraction failed unexpectedly: {e}")
        return

    # 2. TRANSFORM: Normalize and structure the data using Pydantic models
    print("\n--- Starting Data Transformation ---")
    try:
        # NOTE: transform_pokemon_data returns lists of Pydantic Models
        # Ensure that Pydantic models are imported/available (they are used internally by the transformer)
        pokemon_records, type_records, pokemon_type_records = transform_pokemon_data(raw_data)
        print(f"✅ Transformation complete: {len(pokemon_records)} Pokémon, {len(type_records)} unique types prepared.")
    except Exception as e:
        print(f"❌ Transformation failed unexpectedly: {e}")
        return

    # 3. LOAD: Store the transformed data into the SQL database
    print("\n--- Starting Data Loading ---")
    try:
        load_data(pokemon_records, type_records, pokemon_type_records)
        print("✅ Data Loading successful.")
    except Exception as e:
        print(f"❌ Loading failed unexpectedly: {e}")
        return
        
    print("\n=============================================")
    print("✨ PokéPipeline Execution Complete!")
    print("=============================================")


if __name__ == "__main__":
    run_pokepipeline()