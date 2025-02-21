import requests
import concurrent.futures
import time

def check_airdrop(wallet_address):
    url = f"https://claim.rivalz.ai/backend/airdrop/credentials?walletAddress={wallet_address}"
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,id;q=0.8",
        "clq-app-id": "rivalz",
        "content-type": "application/json",
        "dnt": "1",
        "referer": "https://claim.rivalz.ai/unified/eligibility",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    
    retries = 5
    backoff = 1  # Initial backoff in seconds
    for attempt in range(retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"Checked {wallet_address}: {data}")  # Menampilkan hasil di layar
            if int(data.get("tokenQualified", 0)) > 0:
                return wallet_address, data
            return None
        elif response.status_code == 429:
            print(f"Rate limited for {wallet_address}, retrying in {backoff} seconds...")
            time.sleep(backoff)
            backoff *= 2  # Exponential backoff
        else:
            print(f"Failed to fetch data for {wallet_address}, status code: {response.status_code}")
            return None
    return None

def main():
    input_file = "wallets.txt"
    output_file = "qualified_airdrop_results.txt"
    
    with open(input_file, "r") as file:
        wallets = [line.strip() for line in file.readlines() if line.strip()]
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # Kurangi jumlah thread untuk menghindari rate limiting
        futures = {executor.submit(check_airdrop, wallet): wallet for wallet in wallets}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(f"{result[0]}: {result[1]}")
                print(f"Qualified {result[0]}: {result[1]}")
    
    with open(output_file, "w") as file:
        file.write("\n".join(results))
    
    print(f"Qualified results saved to {output_file}")

if __name__ == "__main__":
    main()
