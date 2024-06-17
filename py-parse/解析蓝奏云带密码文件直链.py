import socket
import argparse
import requests
from flask import Flask, request, jsonify

LANZOU_BASE_URL = "www.lanzoux.com"
def get_file_check_info(_file_id):
    base_url = f"https://{LANZOU_BASE_URL}/{_file_id}"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': LANZOU_BASE_URL,
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    }

    response = requests.get(base_url, headers=headers)
    _file_check_code = response.text.split("var skdklds = '")[1].split("';")[0]
    _file_download_id = response.text.split("/ajaxm.php?file=")[1].split("',")[0]
    return _file_check_code, _file_download_id


def get_download_link(_file_id, _file_pws, _file_check_code, _file_download_id):
    download_url = "https://down-load.lanrar.com/file?"

    headers = {
        'Accept': 'application/json, text/javascript, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '116',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'codelen=1; pc_ad1=1',
        'Host': LANZOU_BASE_URL,
        'Origin': f'https://{LANZOU_BASE_URL}',
        'Pragma': 'no-cache',
        'Referer': f'https://{LANZOU_BASE_URL}/{_file_id}',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        'X-Requested-With': 'XMLHttpRequest'
    }

    data = {
        'action': 'downprocess',
        'sign': _file_check_code,
        'p': _file_pws,
        'kd': "1"
    }

    response = requests.post(f'https://{LANZOU_BASE_URL}/ajaxm.php?file={_file_download_id}', data=data, headers=headers)
    json_data = response.json()

    if json_data['zt'] == 1:
        download_link = f"http{download_url[:-1][5:]}/{json_data['url']}"
        return download_link
    else:
        print(f"Error: {json_data['inf']}")

def follow_redirects(_url):
    host = _url.split("://")[1].split("/")[0]
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Host': host,
        'Pragma': 'no-cache',
        'Proxy-Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    }

    session = requests.Session()
    try:
        response = session.get(_url, allow_redirects=False, headers=headers, stream=True)

        while response.status_code == 302:  # 如果是302重定向
            redirect_url = response.headers['Location']
            response = session.get(redirect_url, allow_redirects=False, headers=headers, stream=True)

        if response.status_code == 200:
            final_url = response.url
            return final_url
        else:
            print(f"Failed to follow redirects. Final status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def find_available_port(start_port=5000, end_port=60000):
    """Find an available port within the given range."""
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    raise IOError("No free port found in the specified range.")

def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug

    @app.route('/api/lanzou', methods=['GET'])
    async def provide_download_link():
        """
        API endpoint to generate a download link for a Lanzou file.
        Expects 'file_id' and 'file_pws' as query parameters.
        """
        file_id = request.args.get('file_id')
        file_pws = request.args.get('file_pws')

        if not file_id or not file_pws:
            return jsonify({"error": "Missing 'file_id' or 'file_pws' in the request"}), 400

        try:
            file_check_code, file_download_id = get_file_check_info(file_id)
            download_link = get_download_link(file_id, file_pws, file_check_code, file_download_id)
            download_link = follow_redirects(download_link)

            if download_link:
                return jsonify({"download_link": download_link}), 200
            else:
                return jsonify({"error": "Failed to generate download link"}), 500

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app

def main():
    parser = argparse.ArgumentParser(description="Run the Flask API server.")
    parser.add_argument("--port", type=int, help="The port on which to run the server.", default=None)
    args = parser.parse_args()

    port = args.port if args.port is not None else find_available_port()

    app = create_app(debug=True)
    app.run(port=port)

if __name__ == '__main__':
    main()