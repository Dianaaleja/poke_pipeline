# 🎮 PokePipeline: Robust ETL Data Pipeline

This project is a modular, production-ready ETL pipeline that fetches Pokémon data from the PokeAPI and stores it in a normalized SQLite database with Pydantic validation.

## 🚀 Quick Start

**Prerequisites:** Python 3.9+
```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python app.py
```

Output: `pokemon_data.db` SQLite database with normalized Pokémon data.

## 🏗️ Architecture

### ETL Modules (`src/data_pipeline/`)

| File | Role | Description |
|------|------|-------------|
| `extractor.py` | **Extract** 📥 | Fetches raw JSON from PokeAPI using `requests` |
| `transformer.py` | **Transform** ⚙️ | Normalizes nested JSON and validates with Pydantic models |
| `loader.py` | **Load** 💾 | Manages SQLite database with idempotent `DROP/CREATE` strategy |
| `app.py` | **Orchestration** 🎯 | Executes the E → T → L pipeline sequentially |

### Database Schema

| Table | Type | Fields |
|-------|------|--------|
| `pokemon` | Core Entity | `id` (PK), `name`, `height`, `weight`, `base_experience` |
| `type` | Lookup | `id` (PK), `name` (UNIQUE) |
| `pokemon_type` | Junction (M:N) | `pokemon_id` (FK), `type_id` (FK), `slot` |

**Design:** Many-to-Many relationship handles multiple types per Pokémon. `slot` preserves type ordering (primary/secondary).

## 🎯 Key Design Decisions

### 1. Type Normalization
Uses a global dictionary (`_type_name_to_id`) to assign unique IDs to types, avoiding duplication and enabling efficient queries.
```python
# First encounter: "fire" → ID 1
# Subsequent uses: reuse ID 1
```

### 2. Pydantic Validation
All data validated before database insertion:
- Enforces type safety (`height` must be float)
- Catches errors early (before DB operations)
- Self-documenting data contracts

### 3. Idempotency
`DROP TABLE IF EXISTS` ensures safe re-execution without data conflicts.

## 📋 Assumptions

- **Scope:** Designed for ~150 Pokémon (configurable via `limit` parameter)
- **Storage:** SQLite suitable for demo; production would use PostgreSQL
- **Processing:** Sequential requests; async would improve performance at scale
- **API Reliability:** 10-second timeout with basic error logging

## 🚀 Future Improvements

### High Priority
- ⚡ **Performance:** Async requests (`asyncio`), batch processing, connection pooling
- 🔄 **Incremental Updates:** Delta loading instead of full table drops
- 📊 **Logging:** Structured logging with metrics (records/sec, errors, duration)

### Medium Priority
- 🧪 **Testing:** Unit/integration tests with pytest and mocked API responses
- 🔐 **Resilience:** Retry logic with exponential backoff, circuit breaker pattern
- 📈 **Extended Data:** Add abilities, stats, evolutions, moves

### Nice to Have
- 🎨 **Dashboard:** Streamlit/Flask UI for pipeline monitoring
- 🔧 **Config Management:** Environment variables for API URL, DB path, batch size
- 📚 **API Layer:** FastAPI wrapper for querying normalized data

## 🐳 Docker Support (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```
```bash
docker build -t pokepipeline .
docker run -v $(pwd)/data:/app/data pokepipeline
```

---

**Data Source:** [PokéAPI](https://pokeapi.co/) | **Stack:** Python, Pydantic, SQLite

## 🤝 Contributions
Feel free to open an issue or pull request if you have ideas or improvements for the project.

© [Diana Terraza] - MIT Licens