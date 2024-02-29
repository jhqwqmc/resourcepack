import hashlib
import os,json,time
from aiohttp import ClientSession
from lxml import etree
from flask import Flask, request, jsonify

app = Flask(__name__)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def get_download_url(id):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0_1 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A402 Safari/604.1"
    }
    headers_real_download_url_get = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'down_ip=1',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
    }
    for i in gcache:
        if i == id:
            if int(time.time()) - gcache[i][2] <= 300: #5min过期
                # print('已找到')
                return f"{gcache[i][0]}#{gcache[i][1]}"
            # else:
            #     print('已过期正在重新获取')
    async with ClientSession() as session:
        async with session.get(f'https://wwk.lanzouj.com/tp/{id}', headers=headers) as response:
            html = await response.text()
            html_tree = etree.HTML(html)
            js = str(html_tree.xpath('/html/body/div[1]/script[1]/text()'))
            js = js.replace("'", '').replace("\\n", '').replace("\"", '').replace(" ", '').replace('[', '').replace(']','').split(';')
            download_url = js[3].split('=')[1] + js[5].split('=')[1]
            async with session.get(download_url, headers=headers_real_download_url_get) as real_download_response:
                real_download_url = await real_download_response.read()
                download_url_sha1 = hashlib.sha1(real_download_url).hexdigest()
                t = {str(id):[str(real_download_response.url),str(download_url_sha1),int(time.time())]}
                gcache.update(**t)
                return f"{real_download_response.url}#{download_url_sha1}"

@app.route('/download_url', methods=['GET'])
async def get_download_url_route():
    _id = request.args.get('id')
    if not _id:
        return jsonify({'error': 'Missing parameter: id'}), 400
    try:
        result = await get_download_url(_id)
        return result, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
async def test():
    _id = request.args.get('id')
    if not _id:
        return jsonify({'error': 'Missing parameter: id'}), 400
    try:
        # result = await get_123_url(id)
        result = 'ok'
        return result, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if os.path.exists('cache.json') == False:
        with open('cache.json','w') as f:
            f.write('{}')
    with open('cache.json','r') as f:
        gcache = {}
        gcache = json.loads(f.read())
    app.run(debug=True)
    if gcache != {}:
        with open("cache.json", 'w') as write_f:
            write_f.write(json.dumps(gcache, indent=4, ensure_ascii=False))

