import json

from app.gateway import fetch_flights

if __name__ == "__main__":
    data = fetch_flights(dep_iata="JFK", limit=5)
    with open("sample_response.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Saved sample_response.json")