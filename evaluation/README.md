# Reproducible evaluation

The versioned JSONL fixture exercises every decision class in the rules engine.

```bash
python evaluation/evaluate.py
```

Reported metrics:

- **Rules accuracy:** exact decision match across all fixtures
- **Safety-critical recall:** correct handling of stroke, safety, and low-confidence escalation cases
- **Class coverage:** number of distinct expected decision classes represented

These are deterministic synthetic contract tests. They are intentionally not presented as computer-vision or real-match performance. A production evaluation should use licensed, independently annotated match footage and report event-level precision, recall, calibration, disagreement with officials, and end-to-end latency.
