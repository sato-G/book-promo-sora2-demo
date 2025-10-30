#!/usr/bin/env python3
"""デバッグ用：動画ダウンロードエンドポイントを試す"""
import os
import requests

api_key = os.getenv('OPENAI_API_KEY')
video_id = "video_690371cbfb5881989c25794b6556ba140ee4559bc452327d"

headers = {"Authorization": f"Bearer {api_key}"}
base_url = "https://api.openai.com/v1/videos"

# 試すエンドポイント
endpoints = [
    f"{base_url}/{video_id}/download",
    f"{base_url}/{video_id}/url",
    f"{base_url}/{video_id}/output",
    f"{base_url}/{video_id}/file",
]

for endpoint in endpoints:
    print(f"\n試行: {endpoint}")
    response = requests.get(endpoint, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        content_type = response.headers.get('content-type', '')
        print(f"Content-Type: {content_type}")
        if 'video' in content_type:
            print("✓ 動画ファイルが返ってきました！")
            with open('data/output/test_video.mp4', 'wb') as f:
                f.write(response.content)
            print("保存完了: data/output/test_video.mp4")
            break
        elif 'json' in content_type:
            print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text[:200]}")
