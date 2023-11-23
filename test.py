import requests

chain_url = f"http://localhost:5000/chain"

response = requests.get(chain_url)

print(response)