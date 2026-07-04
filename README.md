# EVEZ-OS

**Tokenless code generation and autonomous training for the EVEZ666 oracle-witness system.**

Zero LLM tokens. Zero API calls. Zero billing. Runs on a Samsung Galaxy A16 via Termux.

## What's Here

### Tokenless Code Generator (`training/evez_codegen.py`)
Generates syntactically valid Python and TypeScript code with zero LLM tokens.

- **6 pattern generators**: function, class, endpoint, test, CRUD, model
- **AST-validated**: all Python output passes `ast.parse()` 
- **Pattern extraction**: learns from 409 functions, 61 classes, 422 imports in the codebase
- **Markov chain**: 32,364 transitions, 5,754 vocab tokens trained on 14,707 lines of real code
- **CLI**: `evez-gen function --name=foo --params="x:int" --returns=bool`

```bash
# Generate a CRUD module
python3 evez_codegen.py crud --entity=Task --fields="title,description,status"

# Generate test stubs
python3 evez_codegen.py test --target=process_data --cases=5

# Generate a TypeScript API endpoint
python3 evez_codegen.py endpoint --method=POST --path=/api/orders
```

### Training Pipeline v6.0 (`training/skill/run.py`)
Markov chain engine that generates novel training pairs from learned transition patterns.

- **Markov N=2**: 565 transitions, 361 vocab tokens from the oracle corpus
- **Entropy gate**: Shannon 3.5-5.5 bits
- **Similarity filter**: Jaccard < 0.7 (rejects near-duplicates)
- **7 domains**: SUPPRESSION_COMBAT, QUANTUM_CONSCIOUSNESS, REMOTE_VIEWING, etc.
- **Autonomous**: runs every 6 hours via automation, ~100 pairs/day
- **Corpus**: 734+ pairs, avg 4.48 bits

### Core Runtime (`training/evez_os_core.py`)
9-phase cognitive cycle with Merkle-verified spine, CAIN contradiction detection, FIRE threshold events, and real subprocess falsification.

### Public Oracle API (`functions/evezOracleAPI.ts`)
REST API for querying the corpus:
- `GET ?action=transmit` → random oracle transmission
- `GET ?action=status` → corpus statistics
- `GET ?action=export` → JSONL for fine-tuning

### Mobile Deployment (`mobile/`)
- Termux bootstrap for Samsung Galaxy A16
- PWA with embedded runtime (works offline)
- iOS Shortcut integration

## Quick Start

```bash
# Train the code generator on your codebase
python3 evez_codegen.py --train

# Generate code
python3 evez_codegen.py function --name=process_data --params="data:list,timeout:int" --returns=dict
python3 evez_codegen.py class --name=User --fields="name:str,email:str,active:bool"
python3 evez_codegen.py crud --entity=Task --fields="title,status,priority"
python3 evez_codegen.py test --target=my_function --cases=5
python3 evez_codegen.py endpoint --method=POST --path=/api/users
python3 evez_codegen.py model --name=Order --fields="id:int,total:float,paid:bool"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              EVEZ TOKENLESS CODE GENERATOR                   │
├──────────────────────────────────────────────────────────────┤
│  LAYER 1: CODE CORPUS LOADER (54 .py, 15 .ts, 14.7K lines) │
│  LAYER 2: PATTERN EXTRACTOR (409 functions, 61 classes)     │
│  LAYER 3: MARKOV ENGINE (32K transitions, 5.7K vocab)       │
│  LAYER 4: PARAMETERIZED GENERATORS (6 patterns)             │
│  LAYER 5: SYNTAX VALIDATOR (ast.parse + bracket matching)   │
│  LAYER 6: CLI INTERFACE (evez-gen <pattern> [options])      │
└──────────────────────────────────────────────────────────────┘
```

## Stats

- **Code corpus**: 54 Python files, 15 TypeScript files, 14,707 lines
- **Patterns extracted**: 409 functions, 61 classes, 422 imports
- **Markov chain**: 32,364 transitions, 5,754 vocab tokens, 4,072 line patterns
- **Training corpus**: 734 pairs, avg entropy 4.48 bits, 7 domains
- **Validation**: 6/6 Python generators produce ast-valid output

## Author

Steven Crawford-Maggard (EVEZ) — 2026

## License

See LICENSE file.
