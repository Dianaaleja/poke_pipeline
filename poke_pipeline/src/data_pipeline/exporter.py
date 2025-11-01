# src/data_pipeline/exporter.py

import pandas as pd
import sqlite3
import os

# Define the path to your SQLite database file
# We now output the data to stdout, so we don't need OUTPUT_FILE
DATABASE_FILE = '../data/pokemon.sqlite' 
JUNCTION_TABLE_NAME = 'pokemon_type' 
TYPE_TABLE_NAME = 'type' 

def process_and_output_type_counts(db_path: str = DATABASE_FILE):
    """
    Connects to the SQLite database, calculates the count of Pokémon per Type,
    and prints the result as CSV to standard output (stdout).
    """
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}.", file=os.sys.stderr)
        print("Please ensure your database is set up or run the previous version of exporter.py once to create the dummy data.", file=os.sys.stderr)
        return

    try:
        conn = sqlite3.connect(db_path)
        
        # SQL Query to count the number of Pokémon for each type
        sql_query = f"""
            SELECT
                T.name AS Type,
                COUNT(J.pokemon_id) AS Count
            FROM
                {TYPE_TABLE_NAME} T
            JOIN
                {JUNCTION_TABLE_NAME} J ON T.id = J.type_id
            GROUP BY
                T.name
            ORDER BY
                Count DESC;
        """
        
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        
    except Exception as e:
        # Imprimimos errores a stderr para no contaminar la salida de datos
        print(f"Error executing SQL query or connecting to DB: {e}", file=os.sys.stderr)
        return

    # NUEVO COMPORTAMIENTO: Imprimir el DataFrame completo como CSV a stdout
    print(df.to_csv(index=False))
    
if __name__ == '__main__':
    # Ensure the 'data' directory exists for DB creation/access
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    process_and_output_type_counts()
