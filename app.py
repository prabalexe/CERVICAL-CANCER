import mysql.connector
import pickle
from flask import Flask,request,jsonify,render_template
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

app=Flask(__name__,template_folder="template")
## import  model and standard scaler pickle

mydb=mysql.connector.connect(
    host='localhost',
    user='root',
    password="123456",
    database='appointment'
)

cursor = mydb.cursor()

model=pickle.load(open('model/model.pkl','rb'))
standard_scaler=pickle.load(open('model/scaler.pkl','rb'))

## Route for home page
@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('/predict'))
    return render_template('index.html')

@app.route('/book_appointment')
def book_appointment():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        date = request.form.get('date')
        time = request.form.get('time')

        # Insert booking into the database
        insert_query = "INSERT INTO bookings (name, email, date, time) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (name, email, date, time))
        mydb.commit()
        return render_template('booking_success.html')
    return render_template('consult.html')


@app.route('/predict',methods=['GET','POST'])
def predict_datapoint():
    if request.method=="POST":
        Age=float(request.form.get('Age'))
        Numberofsexualpartners= float(request.form.get('Number of sexual partners'))
        Firstsexualintercourse= float(request.form.get('First sexual intercourse'))
        Numofpregnancies= float(request.form.get('Num of pregnancies'))
        Smokes= float(request.form.get('Smokes (years)'))
        IUD= float(request.form.get('IUD (years)'))
       
        

        new_data_scaled=standard_scaler.transform([[Age,Numberofsexualpartners,Firstsexualintercourse,Numofpregnancies,Smokes,IUD]])
        result=model.predict(new_data_scaled)

        risk_statement = "No risk"
        if result[0] == 1:
            risk_statement = "Low risk"
        elif result[0] == 2:
            risk_statement = "Medium risk"
        elif result[0] == 3:
            risk_statement = "Risky"
        elif result[0] == 4:
            risk_statement = "Consult a doctor"

        return render_template('home.html', result=result[0], risk_statement=risk_statement)

    else:
        return render_template('home.html')



if __name__=="__main__":
    app.run(host="0.0.0.0")