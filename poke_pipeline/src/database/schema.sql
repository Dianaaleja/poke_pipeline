-- Table 1: pokemon (Core Data)
CREATE TABLE IF NOT EXISTS pokemon (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    high REAL,
    weight REAL,
    base_experience INTEGER
);

-- Table 2: type (Type Dictionary)
-- Note: Assuming that the 'type' data is static and pre-loaded or loaded dynamically but only insertig unique types.
CREATE TABLE IF NOT EXISTS type (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Table 3: pokemon_type (Junction/Mapping Table)
-- Handles the Many-to-Many relationship: One Pokémon has many Types, and one Type has many Pokémon.

CREATE TABLE IF NOT EXISTS pokemon_type (
    pokemon_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    slot INTEGER, -- Indicates the type slot (e.g., primary, secondary)
    PRIMARY KEY (pokemon_id, type_id),
    FOREIGN KEY (pokemon_id) REFERENCES pokemon(id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES type(id) ON DELETE CASCADE 
);