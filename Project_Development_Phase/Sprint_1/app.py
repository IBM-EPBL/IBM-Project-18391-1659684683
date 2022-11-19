from os import getenv
from flask import Flask, render_template, url_for, request, redirect, Markup, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import uuid
import json
import pymysql


load_dotenv()
mysql_user = getenv('MYSQL_USER')
mysql_pass = getenv('MYSQL_PASS')
deploy_url = getenv('DEPLOYMENT_URL')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + \
    mysql_user+':'+mysql_pass+'@localhost/globalsalesdata'
db = SQLAlchemy(app)
app.app_context().push()

app = Flask(__name__)
class Tokens(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    session = db.Column(db.String(36))
    sts = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/generatetoken')


@app.route('/generatetoken', methods=['POST', 'GET'])
def gentoken(active=False, dashboard=False, report=False, story=False, deactivate=False, ml=False, generatetoken=True, activateaccount=False,
             toasts=[], toastdata=[]):
    if request.method == 'POST':
        newid = uuid.uuid4()
        newuser = Tokens(id=str(newid))
        try:
            db.session.add(newuser)
            db.session.commit()
            return {"token_id": str(newid)}
        except:
            return {"token_id": "Error : something when wrong"}
    else:
        return render_template('generatetoken.html', active=active, dashboard=dashboard, report=report, story=story, deactivate=deactivate, ml=ml, generatetoken=generatetoken, activateaccount=activateaccount, toasts=toasts, toastdata=toastdata, deploy_url=deploy_url)


@app.route('/activateacc', methods=['POST', 'GET'])
def activateacc(active=False, dashboard=False, report=False, story=False, deactivate=False, ml=False, generatetoken=False, activateaccount=True,
                toasts=[], toastdata=[]):
    if request.method == 'POST':
        tokenid = request.form['tokenid']
        toactivate = Tokens.query.get_or_404(tokenid)
        if toactivate.sts == False:
            toactivate.sts = True
            sesid = uuid.uuid4()
            toactivate.session = str(sesid)
            db.session.commit()
            toasts = ['success']
            toastdata = [Markup('Successfully activated your account')]
            active = True
            activateaccount = False
            dashboard = True
            res = make_response(render_template('dashboard.html', active=active, dashboard=dashboard, report=report, story=story, deactivate=deactivate,
                                ml=ml, generatetoken=generatetoken, activateaccount=activateaccount, toasts=toasts, toastdata=toastdata, deploy_url=deploy_url))
            res.set_cookie('tokenid', tokenid)
            res.set_cookie('sessionid', str(sesid))
            return res
        else:
            toasts = ['warning']
            toastdata = [Markup('The Token has already been utilized <br> Please <a href="' +
                                deploy_url+'/generatetoken" class="link-text">generate new one</a>')]
            return render_template('activateacc.html', active=active, dashboard=dashboard, report=report, story=story, deactivate=deactivate, ml=ml, generatetoken=generatetoken, activateaccount=activateaccount, toasts=toasts, toastdata=toastdata, deploy_url=deploy_url)
    else:
        return render_template('activateacc.html', active=active, dashboard=dashboard, report=report, story=story, deactivate=deactivate, ml=ml, generatetoken=generatetoken, activateaccount=activateaccount, toasts=toasts, toastdata=toastdata, deploy_url=deploy_url)



if __name__ == "__main__":
    app.run(debug=True)