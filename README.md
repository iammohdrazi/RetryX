# RetryX

**RetryX** is a simple, cross-platform **Retry/Backoff Handler** for Python.  
It allows you to automatically retry functions with configurable backoff strategies, optional jitter, and exception handling.

---

## Features

- Retry functions automatically on failure
- Supports backoff strategies:
  - `fixed`
  - `linear`
  - `exponential`
- Optional jitter to avoid synchronized retries
- Works on Linux, Windows, and macOS
- Minimal, decorator-based API

---

## Installation

You can install RetryX via pip:

```bash
pip install retryx
Or, if using your local version:

bash
Copy code
git clone https://github.com/<your-username>/RetryX.git
cd RetryX
pip install .