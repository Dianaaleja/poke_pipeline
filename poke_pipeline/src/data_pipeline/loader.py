import sqlite3
from typing import List
# Import Pydantic models for type validation and typing
from models.pokemon_data import PokemonModel, TypeModel, PokemonTypeModel

# Define the path for the SQLite database file
DATABASE_FILE = "pokemon_data.db"

def create_tables(conn: sqlite3.Connection):
    """
    Creates the three necessary tables in the SQLite database.
    Implements the DROP TABLE IF EXISTS strategy to ensure idempotency.

    Args:
        conn: The active SQLite database connection object.
    """
    cursor = conn.cursor()

    # --- IDEMPOTENCY STRATEGY: DROP TABLE IF EXISTS ---
    # This ensures that each execution is clean, dropping the tables
    # in reverse order of dependency to prevent foreign key errors.
    
    # 1. Drop the junction table first
    cursor.execute("DROP TABLE IF EXISTS pokemon_type;")
    # 2. Drop the main tables
    cursor.execute("DROP TABLE IF EXISTS pokemon;")
    cursor.execute("DROP TABLE IF EXISTS type;")
    
    print("Old tables dropped (idempotency check).")
    
    # --- TABLE CREATION ---

    # Table 1: pokemon (Core Data)
    cursor.execute("""
    CREATE TABLE pokemon (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        height REAL,
        weight REAL,
        base_experience INTEGER
    );
    """)

    # Table 2: type (Normalized Types)
    cursor.execute("""
    CREATE TABLE type (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    );
    """)

    # Table 3: pokemon_type (Junction Table for M:N Relationship)
    cursor.execute("""
    CREATE TABLE pokemon_type (
        pokemon_id INTEGER,
        type_id INTEGER,
        slot INTEGER,
        PRIMARY KEY (pokemon_id, type_id),
        FOREIGN KEY (pokemon_id) REFERENCES pokemon(id) ON DELETE CASCADE,
        FOREIGN KEY (type_id) REFERENCES type(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    print("Database tables created successfully.")

def load_data(
    pokemon_records: List[PokemonModel],
    type_records: List[TypeModel],
    pokemon_type_records: List[PokemonTypeModel]
):
    """
    Connects to the database, creates (and cleans up) the tables, and inserts
    all transformed Pydantic models.
    
    Args:
        pokemon_records: List of validated PokemonModel objects.
        type_records: List of validated TypeModel objects.
        pokemon_type_records: List of validated PokemonTypeModel objects.
    """
    conn = None # Initialize conn outside the try for the finally block
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        # The call to create_tables now ensures the DROP/CREATE
        create_tables(conn) 
        cursor = conn.cursor()

        # 1. Load Type data
        type_data_tuples = [(t.id, t.name) for t in type_records]
        cursor.executemany(
            "INSERT INTO type (id, name) VALUES (?, ?)",
            type_data_tuples
        )
        print(f"Inserted {len(type_data_tuples)} unique types.")

        # 2. Load Pokémon data
        pokemon_data_tuples = [
            (p.id, p.name, p.height, p.weight, p.base_experience)
            for p in pokemon_records
        ]
        cursor.executemany(
            "INSERT INTO pokemon (id, name, height, weight, base_experience) VALUES (?, ?, ?, ?, ?)",
            pokemon_data_tuples
        )
        print(f"Inserted {len(pokemon_data_tuples)} Pokémon records.")

        # 3. Load Junction Table data (pokemon_type)
        pt_data_tuples = [
            (pt.pokemon_id, pt.type_id, pt.slot)
            for pt in pokemon_type_records
        ]
        cursor.executemany(
            "INSERT INTO pokemon_type (pokemon_id, type_id, slot) VALUES (?, ?, ?)",
            pt_data_tuples
        )
        print(f"Inserted {len(pt_data_tuples)} Pokémon-Type links.")

        conn.commit()

    except sqlite3.Error as e:
        print(f"DATABASE ERROR: An error occurred during data loading: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


# --- Example Integration of the Full Pipeline (for local testing) ---
# NOTE: This section can be omitted in the final script version for production.
# To test locally, you would need to import and run the extractor and transformer first.