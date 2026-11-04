# Results

Pipeline runs generate `latest.json` and `latest.md` here. They are local build artifacts and are not committed because they depend on downloaded NASA data.

Generate them independently with:

```bash
python scripts/results.py
```

The underlying validation records remain in `data/processed/validation/`.
