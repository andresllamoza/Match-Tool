# Code map

## Layout

```
RecordKeeper-Match-Tool/
├── app.py                 # Streamlit application
├── src/
│   ├── matcher.py         # DOL ingest, cache, match(), suggestions
│   └── lookup_log.py      # Lookup audit CSV
├── tests/
│   └── test_lookup_log.py # unittest suite
├── data/                  # Runtime (gitignored)
├── .streamlit/
│   ├── config.toml        # Theme
│   └── secrets.toml.example
├── recordkeeper_mvp.py    # Colab export (reference)
├── requirements.txt
└── runtime.txt            # Python 3.11 for Streamlit Cloud
```

## `src/matcher.py` — key entry points

| Function | Description |
|----------|-------------|
| `load_dol_data()` | Load or build master dataframe (session cache) |
| `match(employer_query, top_n=4)` | Return `list[MatchResult]` |
| `suggest_employers(query)` | Autocomplete suggestions |
| `employer_search_index()` | Distinct rows for typeahead |
| `canonicalize_employer(name)` | Normalization used in matching |

**Dataclasses:** `MatchResult`, `EmployerSuggestion`

**Curated overrides:** `CURATED_EMPLOYER_OVERRIDES` (Disney, Bank of America) — small list for known DOL/name mismatches.

**Matching methods** (examples): `exact_normalized`, `word_boundary`, `fuzzy`, `brand_alias`, `plan_word_boundary`, `curated_override`.

## `app.py` — UI sections

1. Password gate (`check_password`)
2. Employer command search + suggestions (`render_employer_search`)
3. Result card + near misses + feedback
4. Batch CSV upload (`render_batch_lookup`)
5. Lookup attempts expander

## Tests

```bash
python -m unittest tests.test_lookup_log -v
```

Tests mock `_DATAFRAME_CACHE` or use temp `data/` dirs — safe to run in CI without DOL downloads.

## Reference notebook export

[`recordkeeper_mvp.py`](https://github.com/andresllamoza/RecordKeeper-Match-Tool/blob/main/recordkeeper_mvp.py) is the auto-exported Colab notebook. Production logic is maintained in **`src/matcher.py`** only.

---

[← Back to home](index.md)
