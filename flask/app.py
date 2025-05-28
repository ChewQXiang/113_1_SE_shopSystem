from flask import Flask, render_template, request, session, redirect, flash, url_for
from functools import wraps
from dbUtils import add_item, delete_item, update_item, get_items, place_bid, get_item_details, get_bid_history, reset_bids, delete_bids_for_item, add_user, get_user
from werkzeug.security import check_password_hash

app = Flask(__name__, static_folder='static', static_url_path='/')
app.config['SECRET_KEY'] = '123TyU%^&'

# 登入檢查裝飾器
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:  # 確保 session 中的鍵名一致
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

# 用戶註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 檢查用戶是否已存在
        if get_user(username):
            return redirect('/register')
        
        # 新增用戶
        add_user(username, password)
        return redirect('/login')  # 註冊成功後重定向至登入頁面
    
    return render_template('register.html')

# 用戶登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return redirect(url_for('static', filename='loginPage.html'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user(username)
        
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['user_id'] = user['user_id']
            return redirect('/')
        else:
            return redirect('/login')

    return redirect(url_for('static', filename='loginPage.html'))

#登出
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('username', None)
    return redirect('/login')

# 首頁：顯示所有拍賣品
@app.route("/")
@login_required
def index():
    items = get_items()  # 從資料庫中獲取所有拍賣品
    return render_template('item.html', items=items)

# 新增拍賣品
@app.route("/add", methods=['GET', 'POST'])
@login_required
def addItem():
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'description': request.form['description'],
            'base_price': float(request.form['base_price']),
            'user_id': session['user_id']
        }
        add_item(data)
        return redirect('/')
    return render_template('add.html')

# 刪除拍賣品
@app.route("/delete/<int:item_id>")
@login_required
def deleteItem(item_id):
    item = get_item_details(item_id)
    if item['user_id'] != session.get('user_id'):
        return redirect('/')
    
    delete_bids_for_item(item_id)
    delete_item(item_id)
    return redirect('/')

# 更新拍賣品
@app.route("/update/<int:item_id>", methods=['GET', 'POST'])
@login_required
def updateItem(item_id):
    item = get_item_details(item_id)
    if item['user_id'] != session.get('user_id'):
        return redirect('/')

    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'description': request.form['description'],
            'base_price': float(request.form['base_price'])
        }
        update_item(item_id, data)
        return redirect('/')
    
    return render_template('update.html', item=item)

# 查看及競標拍賣品
@app.route("/item/<int:item_id>", methods=['GET', 'POST'])
@login_required
def viewItem(item_id):
    item = get_item_details(item_id)
    if not item:
        return redirect('/')
    
    bids = get_bid_history(item_id)
    if request.method == 'POST':
        bid_amount = float(request.form['bid_amount'])
        success = place_bid(item_id, session['user_id'], bid_amount)  # 使用 user_id
        if success:
            return redirect(f'/item/{item_id}')
        else:
            return redirect(f'/item/{item_id}')

    
    return render_template('view.html', item=item, bids=bids)

if __name__ == "__main__":
    app.run(debug=True)
