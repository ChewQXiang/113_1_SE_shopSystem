import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

try:
    conn = mysql.connector.connect(
        user="root",
        password="",
        host="localhost",
        port=3306,
        database="se_auction"  # 資料庫名稱是 auction_db
    )
    cursor = conn.cursor(dictionary=True)
except mysql.connector.Error as e:
    print(e)
    print("Error connecting to DB")
    exit(1)

# 新增用戶到資料庫，使用加密的密碼
def add_user(username, password):
    hashed_password = generate_password_hash(password)  # 加密密碼
    sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
    cursor.execute(sql, (username, hashed_password))
    conn.commit()

# 根據用戶名查找用戶
def get_user(username):
    sql = "SELECT user_id, username, password FROM users WHERE username = %s"
    cursor.execute(sql, (username,))
    return cursor.fetchone()

# 新增拍賣品
def add_item(data):
    sql = "INSERT INTO items (name, description, base_price, highest_bid, user_id) VALUES (%s, %s, %s, %s, %s)"
    param = (data['name'], data['description'], data['base_price'], None, data['user_id'])
    cursor.execute(sql, param)
    conn.commit()

# 刪除拍賣品
def delete_item(item_id):
    sql = "DELETE FROM items WHERE item_id = %s"  # 使用 item_id 而非 id
    cursor.execute(sql, (item_id,))
    conn.commit()

# 更新拍賣品
def update_item(item_id, data):
    sql = "UPDATE items SET name = %s, description = %s, base_price = %s WHERE item_id = %s"  # 使用 item_id 而非 id
    param = (data['name'], data['description'], data['base_price'], item_id)
    cursor.execute(sql, param)
    conn.commit()

# 獲取拍賣品資料
def get_items():
    sql = "SELECT item_id, name, base_price, highest_bid, user_id FROM items"  # 添加 user_id
    cursor.execute(sql)
    return cursor.fetchall()

# 處理競標
def place_bid(item_id, user_id, bid_amount):
    sql = "SELECT base_price, highest_bid FROM items WHERE item_id = %s"
    cursor.execute(sql, (item_id,))
    item = cursor.fetchone()

    if item and bid_amount > item['base_price'] and (item['highest_bid'] is None or bid_amount > item['highest_bid']):
        # 更新最高出價
        sql = "UPDATE items SET highest_bid = %s WHERE item_id = %s"
        cursor.execute(sql, (bid_amount, item_id))
        # 插入競標記錄
        sql = "INSERT INTO bids (item_id, user_id, bid_amount) VALUES (%s, %s, %s)"
        cursor.execute(sql, (item_id, user_id, bid_amount))
        conn.commit()
        return True
    else:
        return False


# 獲取拍賣品詳細資訊
def get_item_details(item_id):
    sql = "SELECT * FROM items WHERE item_id = %s"  # 使用 item_id 而非 id
    cursor.execute(sql, (item_id,))
    return cursor.fetchone()

# 獲取競標記錄
# dbUtils.py
def get_bid_history(item_id):
    sql = """
    SELECT bids.user_id, bids.bid_amount, bids.timestamp, users.username
    FROM bids
    JOIN users ON bids.user_id = users.user_id
    WHERE bids.item_id = %s
    ORDER BY bids.timestamp DESC
    """
    cursor.execute(sql, (item_id,))
    return cursor.fetchall()


# 重置
def reset_bids():
    sql = "DELETE FROM bids;"
    cursor.execute(sql)
    conn.commit()

# 刪除競拍記錄
def delete_bids_for_item(item_id):
    sql = "DELETE FROM bids WHERE item_id = %s"
    cursor.execute(sql, (item_id,))
    conn.commit()
