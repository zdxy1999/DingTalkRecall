from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/robots', methods=['POST'])
def hello_robots():
    # 获取 JSON 数据
    json_data = request.get_json(silent=True)

    if json_data:
        print(json_data)

        # 获取消息内容
        try:
            content = json_data['text']['content'].replace(' ', '')
            print(f"Received content: {content}")
        except KeyError:
            return jsonify({"error": "Invalid JSON structure"}), 400

        # 这里可以添加你的处理逻辑
        print(f"Processed content: {content}")

        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"error": "No JSON data received"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
