from flask import Flask, request, jsonify, render_template, redirect, url_for, session, make_response, send_file, send_from_directory
from flask_socketio import SocketIO, send, emit
from datetime import datetime, timedelta
from functools import wraps  
import time
import secrets  
import os
import random
import datetime
import logging
from logging.handlers import RotatingFileHandler



app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = secrets.token_hex(32)


# 存储用户信息的文件名
USER_FILE = 'users.txt'


# 从文件中加载用户信息到内存中
def load_users():
    users = {}
    try:
        with open(USER_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) == 2:
                    username, password = parts
                    users[username] = {'username': username, 'password': password}
                else:
                    print(f"不合法的行格式: {line}")
    except FileNotFoundError:
        # 可以处理文件未找到的情况（如果有必要）
        pass
    return users

# 将用户信息保存到文件中
def save_users(users):
    with open(USER_FILE, 'w') as f:
        for user in users.values():
            f.write(f"{user['username']}:{user['password']}\n")

# 在启动时从文件中加载用户信息
users = load_users()

# 设置日志文件路径
log_directory = os.path.join(app.root_path, 'logs')
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, 'requests.log')

# 配置日志处理程序
handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# 在请求之前记录信息的函数
@app.before_request
def log_request_info():
    # 获取IP地址
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()

    # 获取User-Agent字符串
    user_agent = request.headers.get('User-Agent')

    # 记录当前时间
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 使用app.logger记录请求信息
    app.logger.info(f"来自于 {ip_address} 的请求标头 '{user_agent}' 在时间 {current_time}")

@app.route('/robots.txt')
def robots_txt():
    # 返回 robots.txt 的内容或者文件
    return send_from_directory(app.static_folder, 'robots.txt')

	
# 检查登录状态的装饰器
@app.before_request
def require_login():
    allowed_endpoints = ['index', 'login', 'register', 'static', 'robots_txt']
    if 'username' not in session and \
       (request.endpoint is None or \
        (request.endpoint not in allowed_endpoints and \
         not request.endpoint.startswith('static'))):
        session['next'] = request.endpoint if request.endpoint else 'index'
        return redirect(url_for('index'))

		
# 装饰器函数，用于检查会话中的 IP 地址与存储的 IP 地址是否一致
def check_session_ip(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        username = session.get('username')
        stored_ip = session.get('ip_address')
        current_ip = request.remote_addr
        
        if stored_ip and current_ip != stored_ip:
            # 如果当前请求的 IP 地址与存储在会话中的 IP 地址不一致，强制注销会话
            session.clear()  # 清空会话数据
            abort(401)  # 返回 401 错误码，表示未授权访问
        
        return func(*args, **kwargs)
    
    return wrapper
# 主页，用于展示当前连接的 IP 地址
@app.route('/')
@check_session_ip  # 应用装饰器，检查会话中的 IP 地址
def index():
    # 生成带有时间戳的背景图片 URL
    background_image_url = url_for('get_background_image', _timestamp=int(time.time()))
    
    return render_template('index.html', background_image_url=background_image_url, connected_clients=connected_clients, )

connected_clients = {}
# 模拟黑名单，用于存储禁止访问的 IP 地址和相关信息
ip_blacklist = {}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Missing JSON data in request.'}), 400
    
    username = data.get('username')
    password = data.get('password')
    ip_address = request.remote_addr
    
    # 在这里确保 connected_clients 是可见和已定义的
    global connected_clients

    # 记录用户的 IP 地址
    connected_clients[username] = ip_address

    if username in users and users[username]['password'] == password:
        # 登录成功，设置会话
        session['username'] = username
        session['ip_address'] = ip_address
        return redirect(url_for('profile'))
    else:
        return jsonify({'message': 'Login failed. Invalid username or password.'}), 401
		
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    
    app.logger.debug(f"Received username: {username}, password: {password}")
    
    # 获取用户的 IP 地址
    user_ip = request.remote_addr
    
    # 验证用户名和密码
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空。'}), 400
    
    if username in users:
        return jsonify({'error': '用户名已存在。'}), 400
    
    # 将用户信息保存到内存和文件中（包括明文密码和IP地址）
    users[username] = {'username': username, 'password': password, 'ip_address': user_ip}
    save_users(users)
    
    return jsonify({'message': '用户注册成功。'}), 200

# 自定义错误页面处理示例
@app.errorhandler(404)  
def page_not_found(error):  
    return render_template('error/404.html'), 404  
  
@app.errorhandler(500)  
def server_error(error):  
    return render_template('error/500.html'), 500  
  
@app.errorhandler(403)  
def forbidden(error):  
    return render_template('error/403.html'), 403  
  
@app.errorhandler(405)  
def method_not_allowed(error):  
    return render_template('error/405.html'), 405

@app.route('/profile')
@check_session_ip  # 应用装饰器，检查会话中的 IP 地址
def profile():
    username = session.get('username')
    ip = request.remote_addr
    if not username:
        return redirect(url_for('/'))
    return render_template('profile.html', username=username,ip=ip)
	
@app.route('/logout_user', methods=['POST'])
def logout_user():
    if request.method == 'POST':
        session.clear()
        # 可以返回一个 JSON 响应，或者重定向到登录页面或其他页面
        return jsonify({'message': '用户已成功退出登录。'}), 200
    else:
        return render_template('error/405.html'), 405  # 如果客户端使用了不支持的请求方法，可以返回 405 方法不允许的错误码
	
def require_admin(func):  
    @wraps(func)  
    def wrapper(*args, **kwargs):  
        if 'username' not in session:  # 检查是否已登录  
            session['next'] = request.endpoint  # 记录下次需要访问的页面  
            return redirect(url_for('/'))  # 重定向到登录页面  
        if session.get('username') != 'admin':  # 检查是否为管理员  
            return render_template('error/403.html'), 403#非管理员用户重定向到错误页  
        return func(*args, **kwargs)  
    return wrapper

# 管理员页面路由和视图函数
@app.route('/admin')
@require_admin
@check_session_ip  # 应用装饰器，检查会话中的 IP 地址
def admin():
    ip_address = request.remote_addr  # 获取用户的IP地址
    
    # 检查IP地址是否在黑名单中
    if ip_address in ip_blacklist:
        # 如果IP在黑名单中且禁止时间未过期，可以返回禁止访问页面或其他处理
        if time.time() < ip_blacklist[ip_address]:
            return "您的IP地址已被禁止访问。请联系管理员解除禁止。", 403
    
    # 如果未被禁止，继续处理管理员页面的逻辑
    return render_template('admin.html', users=users)

@app.route('/add_user', methods=['POST'])
@require_admin
@check_session_ip  # 应用装饰器，检查会话中的 IP 地址
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空。'}), 400

    if username in users:
        return jsonify({'error': '用户名已存在。'}), 400

    users[username] = {'username': username, 'password': password}
    save_users(users)

    return jsonify({'message': '用户添加成功。'}), 200

@app.route('/delete_user/<username>', methods=['DELETE'])
@require_admin
@check_session_ip  # 应用装饰器，检查会话中的 IP 地址
def delete_user(username):
    if username in users:
        del users[username]
        save_users(users)
        return jsonify({'message': '用户删除成功。'}), 200
    else:
        return jsonify({'error': '用户不存在。'}), 404

@app.route('/change_password/<username>', methods=['PUT'])
@require_admin
@check_session_ip  # 应用装饰器，检查会话中的 IP 地址
def change_password(username):
    data = request.get_json()
    new_password = data.get('new_password')

    if username in users:
        users[username]['password'] = new_password
        save_users(users)
        return jsonify({'message': '密码修改成功。'}), 200
    else:
        return jsonify({'error': '用户不存在。'}), 404

@app.route('/shutdown_server', methods=['POST'])
@require_admin
@check_session_ip  # 应用装饰器，检查会话中的 IP 地址
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
        return 'Server shutting down...'
    else:
        return 'Unable to shutdown server.'

@app.route('/connected_clients', methods=['GET'])
def get_connected_clients():
    clients_list = []
    for client_id, client_ip in connected_clients.items():
        client_info = {
            "user": client_id,  # 客户端用户标识符
            "ip": client_ip  # 客户端IP地址
        }
        clients_list.append(client_info)
    
    return jsonify({
        "clients": clients_list  # 返回包含客户端信息的JSON响应
    })
@app.route('/ban_ip', methods=['POST'])
@require_admin
@check_session_ip  # 应用装饰器，检查会话中的 IP 地址
def ban_ip():
    ip_address = request.json.get('ip_address')
    ban_duration = request.json.get('ban_duration', 16)
    
    if ip_address is None or not isinstance(ban_duration, int) or ban_duration < 0:
        return jsonify({'error': 'IP地址或禁止时长无效。'}), 400
    
    ban_end_time = time.time() + ban_duration
    ip_blacklist[ip_address] = ban_end_time
    
    formatted_time = format_ban_end_time(ban_end_time)
    
    print(f"IP {ip_address} 添加到黑名单，封禁到 {formatted_time}。")
    
    return jsonify({
        'message': f'IP地址 {ip_address} 已被禁止访问 {ban_duration} 秒。',
        'ban_end_time': formatted_time
    }), 200

def format_ban_end_time(ban_end_time):
    ban_end_datetime = datetime.fromtimestamp(ban_end_time)
    formatted_time = ban_end_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time

# 中间件来检查IP是否在黑名单中  
@app.before_request
def check_ip_blacklist():
    ip_address = request.remote_addr
    if ip_address in ip_blacklist and ip_blacklist[ip_address] > time.time():
        formatted_time = format_ban_end_time(ip_blacklist[ip_address])
        return render_template('error/ban.html', bantime=formatted_time), 403
		
#电影功能路由

#与电影相关的功能
# 获取 movies 文件夹中的所有电影文件名
def get_movie_files():
    movies_dir = './movies'  # 修改为 movies 文件夹的路径，根据实际情况修改
    movie_files = []

    # 遍历 movies 文件夹下的所有文件
    for filename in os.listdir(movies_dir):
        # 只获取视频文件（可以根据实际需要扩展）
        if filename.endswith(('.mp4', '.mkv', '.avi', '.mov', '.rmvb')):
            movie_files.append(filename)

    return movie_files

# 电影院页面，用于展示所有电影和播放器
@app.route('/cinema')
@check_session_ip  # 应用装饰器，检查会话中的 IP 地址
def cinema():
    return render_template('cinema.html', movies=get_movie_files())
	
# 视频文件请求处理函数
@app.route('/movies/<filename>')
@check_session_ip  # 应用装饰器，检查会话中的 IP 地址
def movies(filename):
    movies_dir = './movies'  # movies 文件夹的路径，根据实际情况修改
    if filename in get_movie_files():
        return send_file(os.path.join(movies_dir, filename))
    else:
        return render_template('error/404.html'), 404
#电影功能部分完
#api

@app.route('/api')
@require_admin
@check_session_ip  # 应用装饰器，检查会话中的 IP 地址
def api():
    return render_template('api.html')

@app.route('/api/background-image')
@check_session_ip
def get_background_image():
    img_folder = 'background'
    images = [f for f in os.listdir(img_folder) if os.path.isfile(os.path.join(img_folder, f))]

    if images:
        random_image = random.choice(images)
        image_path = os.path.join(img_folder, random_image)
        return send_file(image_path)
    else:
        return 'No images available', 404
		
		
#聊天室部分
@app.route('/chat')
def chat():
    username = session.get('username')
    return render_template('chat.html', username=username)

@socketio.on('connect')
def handle_connect():
    client_ip = request.remote_addr
    print(f'Client connected from {client_ip}')
    connected_clients[request.sid] = client_ip
    emit('status', {'msg': 'User connected'})

@socketio.on('disconnect')
def handle_disconnect():
    client_ip = connected_clients.pop(request.sid, None)
    if client_ip:
        print(f'Client disconnected from {client_ip}')

@socketio.on('send_message')
def handle_message(message):
    client_ip = request.remote_addr
    
    # 检查客户端 IP 是否在黑名单中
    if client_ip in ip_blacklist and ip_blacklist[client_ip] > time.time():
        # 如果在黑名单中且封禁时间尚未结束，可以选择发送一个警告或者错误给客户端
        emit('status', {'msg': 'Your IP is currently blocked from sending messages.'})
        return
    
    # 如果不在黑名单中或者封禁时间已过，继续处理消息
    print('Received message: ' + message['msg'])
    emit('receive_message', {'msg': message['msg'], 'user': message['user'], 'ip': client_ip}, broadcast=True)
	
#文件上传与下载块

@app.route('/file')
def file():
    return render_template('file.html'), 200

# 上传文件
@app.route('/file/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '未选择文件'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'})

    try:
        # 保存文件到指定目录
        file.save(os.path.join('uploads', file.filename))
        return jsonify({'message': '文件上传成功', 'filename': file.filename})
    except Exception as e:
        return jsonify({'error': f'文件上传失败: {str(e)}'})


# 列出指定目录下的文件名
@app.route('/file/list_files')
@check_session_ip  # 应用装饰器，检查会话中的 IP 地址
def list_files():
    files = os.listdir('uploads')
    return jsonify({'files': files})

@app.route('/file/download/<filename>')
def download_file(filename):
    file_path = os.path.join('uploads', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return '文件不存在'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug=False)
