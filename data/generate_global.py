import json
import math
import random

# Haversine distance
def calc_dist(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

airports = [
    {"id": "DEL", "name": "Indira Gandhi Int", "city": "New Delhi", "country": "India", "lat": 28.5562, "lon": 77.1000},
    {"id": "BOM", "name": "Chhatrapati Shivaji", "city": "Mumbai", "country": "India", "lat": 19.0896, "lon": 72.8656},
    {"id": "JFK", "name": "John F. Kennedy Int", "city": "New York", "country": "USA", "lat": 40.6413, "lon": -73.7781},
    {"id": "LAX", "name": "Los Angeles Int", "city": "Los Angeles", "country": "USA", "lat": 33.9416, "lon": -118.4085},
    {"id": "SFO", "name": "San Francisco Int", "city": "San Francisco", "country": "USA", "lat": 37.6213, "lon": -122.3790},
    {"id": "LHR", "name": "Heathrow", "city": "London", "country": "UK", "lat": 51.4700, "lon": -0.4543},
    {"id": "CDG", "name": "Charles de Gaulle", "city": "Paris", "country": "France", "lat": 49.0097, "lon": 2.5479},
    {"id": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany", "lat": 50.0379, "lon": 8.5622},
    {"id": "AMS", "name": "Schiphol", "city": "Amsterdam", "country": "Netherlands", "lat": 52.3105, "lon": 4.7683},
    {"id": "MAD", "name": "Adolfo Suárez", "city": "Madrid", "country": "Spain", "lat": 40.4983, "lon": -3.5676},
    {"id": "DXB", "name": "Dubai Int", "city": "Dubai", "country": "UAE", "lat": 25.2532, "lon": 55.3657},
    {"id": "DOH", "name": "Hamad Int", "city": "Doha", "country": "Qatar", "lat": 25.2731, "lon": 51.6080},
    {"id": "SIN", "name": "Changi", "city": "Singapore", "country": "Singapore", "lat": 1.3644, "lon": 103.9915},
    {"id": "HKG", "name": "Hong Kong Int", "city": "Hong Kong", "country": "China", "lat": 22.3080, "lon": 113.9185},
    {"id": "PEK", "name": "Beijing Capital Int", "city": "Beijing", "country": "China", "lat": 40.0799, "lon": 116.6031},
    {"id": "HND", "name": "Haneda", "city": "Tokyo", "country": "Japan", "lat": 35.5494, "lon": 139.7798},
    {"id": "SYD", "name": "Sydney Airport", "city": "Sydney", "country": "Australia", "lat": -33.9461, "lon": 151.1772},
    {"id": "MEL", "name": "Melbourne Airport", "city": "Melbourne", "country": "Australia", "lat": -37.6690, "lon": 144.8410},
    {"id": "AKL", "name": "Auckland Airport", "city": "Auckland", "country": "New Zealand", "lat": -38.0051, "lon": 174.7832},
    {"id": "YYZ", "name": "Toronto Pearson Int", "city": "Toronto", "country": "Canada", "lat": 43.6777, "lon": -79.6248},
    {"id": "GRU", "name": "Guarulhos Int", "city": "São Paulo", "country": "Brazil", "lat": -23.4356, "lon": -46.4731},
    {"id": "EZE", "name": "Ministro Pistarini Int", "city": "Buenos Aires", "country": "Argentina", "lat": -34.8150, "lon": -58.5348},
    {"id": "JNB", "name": "O. R. Tambo Int", "city": "Johannesburg", "country": "South Africa", "lat": -26.1392, "lon": 28.2460},
    {"id": "CPT", "name": "Cape Town Int", "city": "Cape Town", "country": "South Africa", "lat": -33.9715, "lon": 18.6021},
    {"id": "CAI", "name": "Cairo Int", "city": "Cairo", "country": "Egypt", "lat": 30.1219, "lon": 31.4056},
    {"id": "IST", "name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey", "lat": 41.2753, "lon": 28.7519},
    {"id": "SVO", "name": "Sheremetyevo Int", "city": "Moscow", "country": "Russia", "lat": 55.9726, "lon": 37.4146},
    {"id": "MEX", "name": "Mexico City Int", "city": "Mexico City", "country": "Mexico", "lat": 19.4361, "lon": -99.0719},
    {"id": "BOG", "name": "El Dorado Int", "city": "Bogota", "country": "Colombia", "lat": 4.7016, "lon": -74.1469},
    {"id": "LIM", "name": "Jorge Chávez Int", "city": "Lima", "country": "Peru", "lat": -12.0219, "lon": -77.1143},
    {"id": "BKK", "name": "Suvarnabhumi", "city": "Bangkok", "country": "Thailand", "lat": 13.6900, "lon": 100.7501},
    {"id": "KUL", "name": "Kuala Lumpur Int", "city": "Kuala Lumpur", "country": "Malaysia", "lat": 2.7456, "lon": 101.7099},
    {"id": "CGK", "name": "Soekarno-Hatta Int", "city": "Jakarta", "country": "Indonesia", "lat": -6.1256, "lon": 106.6558},
]

for a in airports:
    a["region"] = "international"

# Create intelligent routes: Hubs to Hubs to keep graph sparse but connected
# We want about 100 interesting edges
routes = []
edges = set()

def add_edge(u_id, v_id):
    if u_id == v_id: return
    pair = tuple(sorted([u_id, v_id]))
    if pair in edges: return
    edges.add(pair)
    
    u = next(a for a in airports if a["id"] == u_id)
    v = next(a for a in airports if a["id"] == v_id)
    
    dist = calc_dist(u["lat"], u["lon"], v["lat"], v["lon"])
    base_cost = math.floor((dist * 6.5) + random.uniform(500, 2000)) # e.g. international pricing pattern (USDish, but we pretend it's global normalized metric)
    
    routes.append({
        "from": u_id,
        "to": v_id,
        "distance_km": math.floor(dist),
        "base_fuel_cost": base_cost
    })

connections = [
    ("JFK", "LHR"), ("JFK", "CDG"), ("JFK", "FRA"), ("JFK", "MEX"), ("JFK", "GRU"), ("JFK", "LAX"), ("JFK", "SFO"),
    ("LAX", "HND"), ("LAX", "SYD"), ("LAX", "MEX"), ("LAX", "SFO"),
    ("LHR", "DXB"), ("LHR", "DEL"), ("LHR", "BOM"), ("LHR", "JNB"), ("LHR", "IST"), ("LHR", "CDG"), ("LHR", "FRA"), ("LHR", "AMS"),
    ("FRA", "DEL"), ("FRA", "DXB"), ("FRA", "SIN"), ("FRA", "IST"), ("FRA", "JNB"),
    ("DXB", "DEL"), ("DXB", "BOM"), ("DXB", "SIN"), ("DXB", "HKG"), ("DXB", "SYD"), ("DXB", "JNB"), ("DXB", "CAI"),
    ("DOH", "LHR"), ("DOH", "JFK"), ("DOH", "SYD"), ("DOH", "DEL"),
    ("DEL", "BOM"), ("DEL", "SIN"), ("DEL", "BKK"), ("DEL", "HND"),
    ("BOM", "SIN"), ("BOM", "KUL"), ("BOM", "CAI"),
    ("SIN", "SYD"), ("SIN", "MEL"), ("SIN", "AKL"), ("SIN", "HND"), ("SIN", "HKG"), ("SIN", "CGK"),
    ("HND", "HKG"), ("HND", "SFO"), ("HND", "SYD"),
    ("SYD", "AKL"), ("SYD", "LAX"), ("SYD", "SFO"),
    ("GRU", "EZE"), ("GRU", "BOG"), ("GRU", "LIM"), ("GRU", "MAD"), ("GRU", "LHR"),
    ("MAD", "EZE"), ("MAD", "BOG"), ("MAD", "LIM"), ("MAD", "LHR"),
    ("JNB", "CPT"), ("JNB", "DXB"), ("JNB", "LHR"),
    ("CAI", "IST"), ("CAI", "LHR"), ("CAI", "DXB"),
    ("IST", "DEL"), ("IST", "JFK"), ("IST", "HKG"),
    ("SVO", "LHR"), ("SVO", "IST"), ("SVO", "PEK"), ("SVO", "DEL"),
    ("PEK", "HKG"), ("PEK", "LHR"), ("PEK", "SFO"),
    ("YYZ", "LHR"), ("YYZ", "FRA"), ("YYZ", "JFK"), ("YYZ", "MEX"),
]

for u, v in connections:
    add_edge(u, v)

# Random filler edges to increase density slightly
hubs = [a["id"] for a in airports]
for _ in range(30):
    u = random.choice(hubs)
    v = random.choice(hubs)
    add_edge(u, v)

data = {
    "meta": {
        "region": "Global (Intercontinental)",
        "currency": "USD",
        "notes": "Global ATC scenario with major international hubs and realistic volumetric pricing."
    },
    "airports": airports,
    "routes": routes
}

with open("d:/All Project/flight-route-optimization/backend/data/airports.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Successfully generated global airports.json!")
