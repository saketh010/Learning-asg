import asyncio
import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_url_blocking(url):
    print(f"Fetching {url}...")
    response = requests.get(url, verify=False)
    time.sleep(1) 
    return f"{url} - Status: {response.status_code}"

async def main():
    urls = [
        "https://www.google.com",
        "https://www.python.org",
        "https://www.github.com"
    ]

    print("Starting Async Tasks")
    start_time = time.perf_counter()

    tasks = [asyncio.to_thread(fetch_url_blocking, url) for url in urls]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.perf_counter()
    
    print("\nResults")
    for result in results:
        if isinstance(result, Exception):
            print(f"Task failed with error: {result}")
        else:
            print(result)

    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())