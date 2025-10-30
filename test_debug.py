#!/usr/bin/env python3
"""デバッグ用：最後の生成結果を確認"""
import os
import requests
import json

api_key = os.getenv('OPENAI_API_KEY')
video_id = "video_690371cbfb5881989c25794b6556ba140ee4559bc452327d"

headers = {"Authorization": f"Bearer {api_key}"}
api_url = "https://api.openai.com/v1/videos"

response = requests.get(f"{api_url}/{video_id}", headers=headers)
print("Status Code:", response.status_code)
print("\nFull Response:")
print(json.dumps(response.json(), indent=2))
