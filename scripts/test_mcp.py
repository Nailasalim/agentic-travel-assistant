import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from tools.hotel_client import get_hotels

hotels = get_hotels("Goa")

print(hotels)
print(type(hotels))