#Importing the Libraries
import numpy as np
from flask import Flask, request,render_template
from flask_cors import CORS
import os
import joblib
import pickle
import flask
import os
import newspaper
from newspaper import Article
import urllib
import pyrebase
from flask import Flask, render_template, request

config = {
    "apiKey": "AIzaSyAGfaTEFrsEUKbm4XG5xNPW4VBtbxUONOI",
    "authDomain": "fakenewsdetection-b11cf.firebaseapp.com",
    "databaseURL": "https://fakenewsdetection-b11cf.firebaseio.com",
    "projectId": "fakenewsdetection-b11cf",
    "storageBucket": "fakenewsdetection-b11cf.appspot.com",
    "messagingSenderId": "265775613130",
    "appId": "1:265775613130:web:85f2a619c59f2b87cda033"
}

with open('model.pickle', 'rb') as handle:
	model = pickle.load(handle)

#Loading Flask and assigning the model variable
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

app = Flask(__name__)
CORS(app)
app=flask.Flask(__name__,template_folder='templates')

#Login
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        email = request.form['user_email']
        password = request.form['user_pwd']
        try:
            auth.sign_in_with_email_and_password(email, password)
            # user_info = auth.sign_in_with_email_and_password(email, password)
            # account_info = auth.get_account_info(user_info['idToken'])
            # if not account_info['user'][0]['emailVerified']:
            #     verify_message = 'Please verify your email'
            #     return render_template('index.html', umessage=verify_message)
            return render_template('main.html')
        except:
            unsuccessful = "Please check your credentials"
            return render_template('index.html', umessage=unsuccessful)
    return render_template('index.html')

#Signup
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        pwd0 = request.form['user_pwd0']
        pwd1 = request.form['user_pwd1']
        if pwd0 == pwd1:
            try:
                email = request.form['user_email']
                password = request.form['user_pwd1']
                new_user = auth.create_user_with_email_and_password(email, password)
                auth.send_email_verification(new_user['idToken'])
                return render_template('verify_email.html')
            except:
                existing_account = 'This email is already used'
                return render_template('create_account.html', exist_message=existing_account)
    return render_template('create_account.html')

#reset password
@app.route('/reset_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['user_email']
        auth.send_password_reset_email(email)
        return render_template('verify_reset_password.html')
    return render_template('reset_password.html')

#Receiving the input url from the user and using Web Scrapping to extract the news content
@app.route('/predict',methods=['GET','POST'])
def predict():
    url =request.get_data(as_text=True)[5:]
    url = urllib.parse.unquote(url)
    article = Article(str(url))
    article.download()
    article.parse()
    article.nlp()
    news = article.summary
    #Passing the news article to the model and returing whether it is Fake or Real
    pred = model.predict([news])
    return render_template('main.html', prediction_text='The news is "{}"'.format(pred[0]))
    
if __name__=="__main__":
    port=int(os.environ.get('PORT',5000))
    app.run(port=port,debug=True,use_reloader=False)