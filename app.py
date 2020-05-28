import sqlite3
import flask

def get_months():
    db = get_db()
    rows = db.execute("SELECT DISTINCT date FROM Transactions")
    lst = []
    for tur in rows:
        day = tur[0].split('-')
        month = day[1]
        year = day[0]
        yearmonth = year+'-'+month
        if yearmonth not in lst:
            lst += [year+'-'+month]
    db.close()
    return lst
app = flask.Flask(__name__)

def get_db():
    db = sqlite3.connect('jpjcSalon.db')
    db.row_factory = sqlite3.Row
    return db

@app.route('/')
def home():
    return flask.render_template("index.html")

@app.route('/addmember')
def addmember():
    return flask.render_template("addmember.html")

@app.route('/memberadded', methods=['POST']) ##new entry
def memberadded(): 
    n = flask.request.form['memberName']
    g = flask.request.form['gender']
    e = flask.request.form['email']
    c = flask.request.form['contact']
    a = flask.request.form['address']
    db = get_db()
    db.execute('INSERT into Member('+
               'memberName,gender,email,contact,address)'+
               'VALUES (?,?,?,?,?)',(n,g,e,c,a))
    db.commit()
    db.close()
    return flask.render_template('added.html',n=n)
@app.route('/addtransaction')
def addtransaction():
    return flask.render_template("addtransaction.html")
@app.route('/transactionadded', methods=['GET','POST'])
def transactionadded():
    style_code = ['cut1','cut2','cut3','colour','high1','high2','perm','rebond','treat']
    style = ['Cut(short length)','Cut(medium length)','Cut(long length)','Colour','Highlight(half head)','Highlight(full head)','Perm','Rebonding','Treatment']
    n = flask.request.form['name']
    d = flask.request.form['date']
    m = flask.request.form['memid']
    t = flask.request.form.getlist('styles')
    total = 0.0
    db = get_db()
    db.commit()
    i = db.execute("SELECT seq FROM sqlite_sequence WHERE name = 'Transactions'").fetchall()
    i = i[0][0]
    for items in t:
        indexing = style_code.index(items)
        db.execute('INSERT INTO TransactionDetail('+
               'invoiceID, type) VALUES (?,?)',(i,style[indexing]))
        db.commit()
        print("THIS IS STYLE:",style[indexing])
        c = db.execute("SELECT price FROM Service WHERE type = (?)",(style[indexing],)).fetchall()
        c = c[0][0]
        total += c
    
    membership = db.execute("SELECT memberName FROM Member WHERE memberID = (?)",(m,)).fetchall()
    if membership[0][0] == n:
        discounted = 0.9
    else:
        discounted = 1.0
    payable = total * discounted
    db.execute('INSERT INTO Transactions('+
               'memberID,name,date,totalamount) VALUES (?,?,?,?)',(m,n,d,payable))
    db.commit()
    db.close()
    return flask.render_template('added.html',n=n)

@app.route('/viewdailyTransaction')
def viewdailyTransaction():
    return flask.render_template('viewdailytransaction.html')
@app.route('/viewTransaction',methods=['POST'])
def viewtransaction():
    d = flask.request.form['date']
    db = get_db()
    rows = get_db().execute('SELECT * FROM Transactions WHERE date = (?)',(d,)).fetchall()
    db.close()
    return flask.render_template('viewtransaction.html',rows=rows)
@app.route('/updatemember')
def updatemember():
    return flask.render_template('updatemember.html')
@app.route('/updated',methods=["POST"])
def updated():
    m = flask.request.form['mem']
    e = flask.request.form['email']
    c = flask.request.form['contact']
    db = get_db()
    if e != '-':
        db.execute('UPDATE Member SET email = (?) WHERE memberID = (?)',(e,m))
        db.commit()
    if c != '-':
        db.execute('UPDATE Member SET contact = (?) WHERE memberID = (?)',(c,m))
        db.commit()
    db.close()
    return flask.render_template('contentupdated.html',m=m)
@app.route('/viewhistory')
def viewhistory():
    return flask.render_template('viewhistory.html')
@app.route('/findhistory',methods=["POST"])
def memberhistory():
    m = flask.request.form['mem']
    db = get_db()
    rows = db.execute("SELECT name,date,totalamount FROM Transactions WHERE memberID = (?)",(m,)).fetchall()
    db.close()
    return flask.render_template('memberhistory.html',rows=rows,g=rows[0][0])

@app.route('/calculaterevenue')
def viewrevenue():
    lst = get_months()
    return flask.render_template('viewrevenue.html',lst=lst)
        
@app.route('/searchmonthly',methods=['POST'])
def searchmonthly():
    months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    o = flask.request.form['choice']
    db = get_db()
    rows = db.execute("SELECT invoiceID,totalamount,date FROM Transactions WHERE date BETWEEN date((?)) AND date((?))",(o+'-01',o+'-31')).fetchall()
    total = 0
    for row in rows:
        total += float(row[1])
    year,month,day = rows[0][2].split('-')
    month = months[int(month)-1]
    db.close()
    return flask.render_template('searchmonthly.html',rows=rows,total=total,year=year,month=month)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
