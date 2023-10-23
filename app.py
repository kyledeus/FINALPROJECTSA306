from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')


myconn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='dbstore'
)



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/verify', methods=['POST', 'GET'])
def verify():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        mycursor = myconn.cursor()
        sql = "SELECT * FROM tblcustomers WHERE email=%s AND password=%s"
        data = (email, password)
        mycursor.execute(sql, data)
        myresult = mycursor.fetchall()

        if myresult:
            mycursor1 = myconn.cursor()
            sql = "SELECT * FROM tblproducts"
            mycursor1.execute(sql)
            myresult1 = mycursor1.fetchall()

            return render_template('catalog.html', user=myresult, products=myresult1)
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/save', methods=['POST', 'GET'])
def save():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        contactno = request.form['contactno']
        email = request.form['email']
        password = request.form['password']

        mycursor = myconn.cursor()
        sql = "INSERT INTO tblcustomers (name, address, contactno, email, password) VALUES (%s,%s,%s,%s,%s)"
        data = (name, address, contactno, email, password)
        mycursor.execute(sql, data)
        myconn.commit()

        return render_template('login.html')



@app.route('/catalog/<customerid>')
def catalog(customerid):
    mycursor = myconn.cursor()
    sql = "SELECT * FROM tblcustomers WHERE customerid=%s"
    data = (customerid,)
    mycursor.execute(sql, data)
    myresult = mycursor.fetchall()

    mycursor2 = myconn.cursor()
    sql = "SELECT * FROM tblproducts"
    mycursor2.execute(sql)
    myresult2 = mycursor2.fetchall()



    return render_template('catalog.html', user=myresult, products=myresult2)


@app.route('/order/<productid>,<customerid>', methods=['POST'])
def order(productid, customerid):
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        size = request.form['size']
        topping = request.form['topping']  # Get selected topping
        crust = request.form['crust']  # Get selected crust

        # Retrieve product details from the database based on productid
        mycursor = myconn.cursor()
        sql = "SELECT * FROM tblproducts WHERE productid=%s"
        data = (productid,)
        mycursor.execute(sql, data)
        product = mycursor.fetchone()

        # Extract necessary details from the product
        name = product[1]
        price = product[2]
        amount = price * quantity
        date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        # Insert order data into tblorders table
        mycursor1 = myconn.cursor()
        sql = "INSERT INTO tblorders (date, productid, name, price, quantity, size, amount, customerid, topping, crust) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        data = (date, productid, name, price, quantity, size, amount, customerid, topping, crust)
        mycursor1.execute(sql, data)
        myconn.commit()

    # Rest of your code...

    mycursor2 = myconn.cursor()
    sql = "SELECT * FROM tblorders WHERE customerid=%s"
    data = (customerid,)
    mycursor2.execute(sql, data)
    myresult2 = mycursor2.fetchall()
    total = 0
    for t in myresult2:
        total += t[4]

    mycursor3 = myconn.cursor()
    sql = "SELECT * FROM tblcustomers WHERE customerid=%s"
    data = (customerid,)
    mycursor3.execute(sql, data)
    myresult3 = mycursor3.fetchall()

    return render_template('orders.html', user=myresult3, orders=myresult2, total=total)


@app.route('/orders/<customerid>')
def orders(customerid):
    mycursor = myconn.cursor()
    sql = "SELECT * FROM tblorders WHERE customerid=%s"
    data = (customerid,)
    mycursor.execute(sql, data)
    myresult = mycursor.fetchall()
    total = 0
    for t in myresult:
        total += t[4]

    mycursor1 = myconn.cursor()
    sql = "SELECT * FROM tblcustomers WHERE customerid=%s"
    data = (customerid,)
    mycursor1.execute(sql, data)
    myresult1 = mycursor1.fetchall()

    return render_template('orders.html', user=myresult1, orders=myresult, total=total)


@app.route('/delete/<orderno>,<customerid>')
def delete(orderno, customerid):
    mycursor = myconn.cursor()

    sql = "DELETE FROM tblorders WHERE orderid=%s"
    data = (orderno,)
    mycursor.execute(sql, data)
    myconn.commit()

    mycursor1 = myconn.cursor()
    sql = "SELECT * FROM tblorders WHERE customerid=%s"
    data = (customerid,)
    mycursor1.execute(sql, data)
    myresult1 = mycursor1.fetchall()
    total = 0
    for t in myresult1:
        total += t[4]

    mycursor3 = myconn.cursor()
    sql = "SELECT * FROM tblcustomers WHERE customerid=%s"
    data = (customerid,)
    mycursor3.execute(sql, data)
    myresult3 = mycursor3.fetchall()

    return render_template('orders.html', user=myresult3, orders=myresult1, total=total)







from flask import request

@app.route('/update/<int:orderno>,<int:customerid>', methods=['GET', 'POST'])
def update(orderno, customerid):
    if request.method == 'POST':

        quantity = int(request.form['quantity'])
        size = request.form['size']
        topping = request.form['topping']
        crust = request.form['crust']


        mycursor = myconn.cursor()
        sql = "UPDATE tblorders SET quantity=%s, size=%s, topping=%s, crust=%s WHERE orderid=%s"
        data = (quantity, size, topping, crust, orderno)
        mycursor.execute(sql, data)
        myconn.commit()


        return redirect(f'/orders/{customerid}')
    else:

        mycursor = myconn.cursor()
        sql = "SELECT * FROM tblorders WHERE orderid=%s"
        data = (orderno,)
        mycursor.execute(sql, data)
        order_details = mycursor.fetchone()

        return render_template('update.html', order=order_details, customerid=customerid)









if __name__ == '__main__':
    app.run(debug=True)