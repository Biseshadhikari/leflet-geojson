import requests
import time
import pandas as pd
from django.db import transaction
from .models import ElectionResult, FederalConstituency

# ---- CONFIG ----
BASE_URL = "https://result.election.gov.np/JSONFiles/Election2079/HOR/FPTP/HOR-{}-{}.json"
MAX_DISTRICTS = 77
MAX_CONSTITUENCIES = 5
ELECTION_YEAR = 2079

# Optional static lat/lng for mapping
location_coords = {
    "बुटवल": (27.6917, 83.4486),
    "सिद्धार्थनगर": (27.5105, 83.4476),
    "देवदह": (27.6833, 83.5333),
    "ओमसतिया": (27.616, 83.386),
    "सियारी": (27.65, 83.3),
    "सम्मरीमाई": (27.57, 83.53),
    "मायादेवी": (27.567, 83.517),
    "कञ्चन": (27.535, 83.443),
    "गैडहवा": (27.580, 83.297),
    "रोहिणी": (27.507, 83.593),
}

def get_lat_lng(address):
    if isinstance(address, str):
        for key, val in location_coords.items():
            if key in address:
                return val
    return None, None

@transaction.atomic
def run_import():
    all_saved = 0

    for district in range(1, MAX_DISTRICTS + 1):
        for constituency in range(1, MAX_CONSTITUENCIES + 1):
            url = BASE_URL.format(district, constituency)
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    print(f"⚠️ Skipped (Not Found): {url}")
                    continue

                candidates = response.json()
                if not isinstance(candidates, list):
                    continue

                constituency_id = f"HOR-{district}-{constituency}"
                constituency_obj, _ = FederalConstituency.objects.get_or_create(
                    id=constituency_id,
                    defaults={"name": constituency_id}
                )

                for c in candidates:
                    lat, lng = get_lat_lng(c.get("ADDRESS", ""))

                    ElectionResult.objects.create(
                        election_type='federal',
                        constituency=constituency_obj,
                        candidate_name=c.get("CandidateName"),
                        party=c.get("PoliticalPartyName", ""),
                        symbol=c.get("SymbolName", ""),
                        votes=c.get("TotalVoteReceived") or 0,
                        address=c.get("ADDRESS"),
                        gender=c.get("Gender"),
                        age=c.get("Age") if c.get("Age") else None,
                        qualification=c.get("QUALIFICATION"),
                        remarks=c.get("Remarks"),
                        year=ELECTION_YEAR,
                        lat=lat,
                        lng=lng
                    )
                    all_saved += 1

                print(f"✅ Imported {len(candidates)} from {url}")

            except Exception as e:
                print(f"❌ Error fetching {url}: {e}")

            time.sleep(0.25)

    print(f"\n🎉 Done. {all_saved} candidates saved.")

