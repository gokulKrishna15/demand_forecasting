import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
H2O_MAX_MEM = os.getenv("H2O_MAX_MEM", "4G")
VECTORSTORE_DIR = Path(os.getenv("VECTORSTORE_DIR", BASE_DIR / "backend" / "track_b_rag" / "vectorstore"))
MODELS_DIR = BASE_DIR / "saved_models"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# Dataset file paths (placeholders)
MAINTENANCE_DATA_FILE = DATA_DIR / "bsl_maintenance_spares.csv"
TENDER_RFP_FILE = DATA_DIR / "bsl_tender_rfp.json"
VENDOR_BIDS_FILE = DATA_DIR / "bsl_vendor_bids.json"
FERRO_ALLOYS_DATA_FILE = DATA_DIR / "bsl_ferro_alloys_market.csv"
