import time
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import ElectionResult, FederalConstituency

GOOGLE_API_KEY = "YOUR_REAL_API_KEY"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
BASE_URL = "https://result.election.gov.np/JSONFiles/Election2079/HOR/FPTP/HOR-{}-{}.json"
MAX_DISTRICTS = 77
MAX_CONSTITUENCIES = 5
ELECTION_YEAR = 2079

class Command(BaseCommand):
    help = "Import and geocode election winners only"

    def geocode_address(self, address):
        if not address:
            return None, None
        try:
            query = f"{address}, Nepal"
            response = requests.get(GEOCODE_URL, params={'address': query, 'key': GOOGLE_API_KEY})
            data = response.json()
            if data['status'] == 'OK':
                location = data['results'][0]['geometry']['location']
                return location['lat'], location['lng']
            else:
                self.stdout.write(f"⚠️ Geocode failed for {address}: {data['status']}")
        except Exception as e:
            self.stderr.write(f"❌ Exception in geocoding {address}: {e}")
        return None, None

    @transaction.atomic
    def handle(self, *args, **kwargs):
        all_saved = 0
        for district in range(1, MAX_DISTRICTS + 1):
            for constituency in range(1, MAX_CONSTITUENCIES + 1):
                url = BASE_URL.format(district, constituency)
                try:
                    response = requests.get(url)
                    if response.status_code != 200:
                        self.stdout.write(f"⚠️ Skipped: {url}")
                        continue

                    candidates = response.json()
                    if not isinstance(candidates, list):
                        continue

                    constituency_id = f"HOR-{district}-{constituency}"
                    constituency_obj, _ = FederalConstituency.objects.get_or_create(
                        id=constituency_id, defaults={"name": constituency_id}
                    )

                    for c in candidates:
                        # Safe extraction
                        remarks = (c.get("Remarks") or "").strip()
                        is_winner = remarks == "निर्वाचित"
                        address = (c.get("ADDRESS") or "").strip()
                        lat = lng = None

                        if is_winner and address:
                            lat, lng = self.geocode_address(address)
                            time.sleep(0.25)  # Google API rate limit

                        ElectionResult.objects.create(
                            election_type='federal',
                            constituency=constituency_obj,
                            candidate_name=c.get("CandidateName") or "",
                            party=c.get("PoliticalPartyName") or "",
                            symbol=c.get("SymbolName") or "",
                            votes=c.get("TotalVoteReceived") or 0,
                            address=address or None,
                            gender=c.get("Gender") or "",
                            age=c.get("Age") or None,
                            qualification=c.get("QUALIFICATION") or "",
                            remarks=remarks,
                            year=ELECTION_YEAR,
                            lat=lat,
                            lng=lng
                        )
                        all_saved += 1

                    self.stdout.write(f"✅ Imported {len(candidates)} from {url}")
                except Exception as e:
                    self.stderr.write(f"❌ Error on {url}: {e}")

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Finished. Saved {all_saved} results."))
