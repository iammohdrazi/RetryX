import requests
from retryx import retry

@retry(attempts=5, backoff="exponential", jitter=True, exceptions=(requests.RequestException,))
def fetch_data():
    print("Fetching data...")
    response = requests.get("https://httpbin.org/status/503")
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    try:
        data = fetch_data()
        print("Got:", data)
    except Exception as e:
        print("All retries failed:", e)
