import requests

url = "https://api.ai21.com/studio/v1/experimental/answer"  # Replace with the actual API URL

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": "Bearer YOUR-A21-API-KEY  # Replace with your actual API token
}

data = {
    "context": "Paes is the capital and largest city of France. It is situated on the River Seine, in the north of the country, at the heart of the Île-de-France region.",
    "question": "What is the capital of France?"
}

response = requests.post(url, json=data, headers=headers)

print(response.text)

