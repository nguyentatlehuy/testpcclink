from flask import Flask, render_template, jsonify, request
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'addresses'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cities')
def cities():
    cur = mysql.connection.cursor()
    cur.execute("SELECT tentinhthanh FROM tinhthanh")
    cities = cur.fetchall()
    cur.close()
    return jsonify(cities)

@app.route('/districts/<city>')
def districts(city):
    cur = mysql.connection.cursor()
    cur.execute("SELECT Ten_quan FROM district WHERE ID_tinh_thanh =(SELECT IDtinhthanh FROM tinhthanh WHERE tentinhthanh = %s)", (city,))
    districts = cur.fetchall()
    cur.close()
    return jsonify(districts)

@app.route('/wards/<district>')
def wards(district):
    cur = mysql.connection.cursor()
    cur.execute("SELECT Ten_phuong_xa FROM ward_code WHERE ID_quan_huyen=(SELECT ID_quan_huyen FROM district WHERE Ten_quan = %s)", (district,))
    wards = cur.fetchall()
    cur.close()
    return jsonify(wards)

@app.route('/save_address', methods=['POST'])
def save_address():
    city = request.form['city']
    district = request.form['district']
    ward = request.form['ward']
    address = request.form['address']

    cur = mysql.connection.cursor()
    cur.execute("SELECT IDtinhthanh FROM tinhthanh WHERE TenTinhThanh = %s", (city,))
    ward_id = cur.fetchone()
    cur.close()
    if ward_id:
        ward_id = ward_id[0]
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT ID_quan_huyen FROM district WHERE Ten_quan = %s", (district,))
    wards_id = cur.fetchone()
    cur.close()
    if wards_id:
        wards_id = wards_id[0]
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT ID_phuong_xa FROM ward_code WHERE Ten_phuong_xa = %s  AND ID_tinh_thanh = %s AND ID_quan_huyen = %s", (ward, ward_id, wards_id))
    wardss_id = cur.fetchone()
    cur.close()
    if wardss_id:
        wardss_id = wardss_id[0]

    combined_data = str(ward_id) + ", " + str(wards_id) + ", " + str(wardss_id) + ", " + address
    return jsonify(combined_data)

@app.route('/search', methods=['POST'])
def search():
    search_value = request.form['search']
    # tinh
    cur = mysql.connection.cursor()
    cur.execute("SELECT TenTinhThanh  FROM tinhthanh WHERE lower(TenTinhThanh) = LOWER(%s) OR lower(Viettat) = LOWER(%s)  OR LOWER(TenTinhThanh) REGEXP %s", (search_value,search_value, search_value))
    ans = cur.fetchall()
    cur.close()
    results = [item[0] for item in ans]

    #quan huyen
    cur = mysql.connection.cursor()
    cur.execute("SELECT Ten_day_du  FROM district WHERE lower(Ten_quan) = LOWER(%s) OR lower(Viettat) = LOWER(%s)  OR LOWER(Ten_quan) REGEXP %s", (search_value,search_value, search_value))
    huyen = cur.fetchall()
    cur.close()
    results += [item[0] for item in huyen]
    
    #quan huyen
    cur = mysql.connection.cursor()
    cur.execute("SELECT ID_tinh_thanh  FROM ward_code_2 WHERE lower(Ten_phuong_xa) = LOWER(%s)  OR lower(Viettat) = LOWER(%s)   OR LOWER(Ten_phuong_xa) REGEXP %s", (search_value,search_value, search_value))
    xa = cur.fetchall()
    cur.close()

    results += [item[0] for item in xa]

    return jsonify(results)

    # Thực hiện xử lý tìm kiếm với HeidiSQL ở đây
    # Ví dụ: thêm câu truy vấn SQL để lấy dữ liệu dựa trên giá trị tìm kiếm
    # return "Dữ liệu tìm kiếm với giá trị '{}': ...".format(search_value)

if __name__ == '__main__':
    app.run(debug=True)
