from flask import Flask, request, jsonify
from flask_cors import CORS
from validador_m3u8 import check_channel

app = Flask(__name__)
CORS(app)

@app.route('/validateM3U8', methods=['POST'])
def check_url():
    data = request.get_json()
    urlInput = data.get('url')
    url, load_time, is_valid, info = check_channel(urlInput)
    print(f"URL: {url}")
    print(f"Load time: {load_time} s")
    print(f"Valid: {is_valid}")
    print(f"Info: {info}")
    return jsonify({'url': url, 'load_time': load_time, 'is_valid': is_valid, 'info': info})
