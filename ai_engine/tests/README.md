# AI Engine Tests

This folder contains tests for adversarial-awareness behavior and contract stability.

## Current Tests

- `test_adversarial.py`
  - Benign message should not trigger adversarial alert.
  - Confidence manipulation with probing context should trigger.
  - Rapid probing from the same IP should trigger.

## Run

```bash
python -m ai_engine.tests.test_adversarial
```

If package imports fail from direct path execution, run as a module from project root.
