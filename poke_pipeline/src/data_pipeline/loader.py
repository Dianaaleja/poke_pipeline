import sqlite3
from typing import List
# Importamos Pydantic models para validación de tipos y tipado
from models.pokemon_data import PokemonModel, TypeModel, PokemonTypeModel

# Define la ruta para el archivo de base de datos SQLite
DATABASE_FILE = "pokemon_data.db"

def create_tables(conn: sqlite3.Connection):
    """
    Crea las tres tablas necesarias en la base de datos SQLite.
    Implementa la estrategia DROP TABLE IF EXISTS para garantizar la idempotencia.

    Args:
        conn: El objeto de conexión a la base de datos SQLite activo.
    """
    cursor = conn.cursor()

    # --- ESTRATEGIA DE IDEMPOTENCIA: DROP TABLE IF EXISTS ---
    # Esto asegura que cada ejecución es limpia, eliminando las tablas
    # en orden inverso de dependencia para evitar errores de llave foránea.
    
    # 1. Eliminar la tabla de unión primero
    cursor.execute("DROP TABLE IF EXISTS pokemon_type;")
    # 2. Eliminar las tablas principales
    cursor.execute("DROP TABLE IF EXISTS pokemon;")
    cursor.execute("DROP TABLE IF EXISTS type;")
    
    print("Old tables dropped (idempotency check).")
    
    # --- CREACIÓN DE TABLAS ---

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
    Conecta a la base de datos, crea (y limpia) las tablas, e inserta
    todos los modelos Pydantic transformados.
    
    Args:
        pokemon_records: Lista de objetos PokemonModel validados.
        type_records: Lista de objetos TypeModel validados.
        pokemon_type_records: Lista de objetos PokemonTypeModel validados.
    """
    conn = None # Inicializar conn fuera del try para el bloque finally
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        # La llamada a create_tables ahora garantiza el DROP/CREATE
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
# NOTA: Esta sección puede ser omitida en la versión final del script para producción.
# Para probar localmente, necesitarías importar y ejecutar el extractor y transformador primero.
