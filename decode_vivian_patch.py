import base64, gzip, sys
from pathlib import Path

source = Path(sys.argv[1]).read_text(encoding="ascii").strip()
destination = Path(sys.argv[2])
# Recover the one-character insertion in the compressed payload; gzip CRC validates the exact result.
for index in range(len(source)):
    candidate = source[:index] + source[index + 1:]
    try:
        payload = gzip.decompress(base64.b64decode(candidate, validate=True))
    except Exception:
        continue
    if payload.startswith(b"from pathlib import Path"):
        destination.write_bytes(payload)
        print(f"Recovered Vivian patch ({len(payload)} bytes) after correcting one inserted base64 character.")
        break
else:
    raise SystemExit("Could not recover the Vivian patch payload.")
