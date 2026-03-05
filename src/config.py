from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "anime_dataset_new.csv"

# Recommendation controls
FUZZY_MATCH_THRESHOLD = 60
TITLE_MATCH_THRESHOLD = 55
TOP_N_DEFAULT = 10

# Similarity weights for final ranking
SIMILARITY_WEIGHTS = {
	"genre": 0.40,
	"description": 0.35,
	"season": 0.10,
	"numeric": 0.15,
}
