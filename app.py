from flask import Flask,render_template,request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
# import psycopg2 # uncomment for postgres
import shutil, sys

app = Flask(__name__)
## Change bp:log to appropriate user/password
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bp:log@localhost:5432/health_stats'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data//health_stats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisismysecret'
db = SQLAlchemy(app)
title='Blood Pressure Monitoring Log'

# Create our database model
class BP_Log(db.Model):
    __tablename__ = "bp_log"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(8), nullable=False)
    time = db.Column(db.String(7), nullable=False)
    SYS = db.Column(db.Integer, nullable=False)
    DIA = db.Column(db.Integer, nullable=False)
    Pulse = db.Column(db.Integer, nullable=False)

    def __init__(self, date, time, sys, dia, pulse):
        self.date = date
        self.time = time
        self.SYS = sys
        self.DIA = dia
        self.Pulse= pulse

def compute_averages(logs):
    """ Compute average SYS, DIA and Pulse readings """
    totsys = totdai = totpulse = 0
    for log  in logs:
        totsys += log.SYS
        totdai += log.DIA
        totpulse += log.Pulse
    sys = round(totsys / len(logs))
    dia = round(totdai / len(logs))
    pulse = round(totpulse / len(logs))
    return sys, dia, pulse

# Landing Page
@app.route('/')
def home():
    return render_template('landing.html', title=title)

# List all/Add a new BP log
@app.route('/logs', methods=['GET', 'POST'])
def bplogs():
    if request.method == 'POST':
        # Set date - none by default
        if not request.form["start-date"] and not request.form['end-date']:
            # get all detail logs
            logs = BP_Log.query.all()
            # Get averages from SQL View bp
            avgs = db.engine.execute("select * from bp")
        elif request.form['start-date'] and not request.form['end-date']:
            # find all detail logs from start date to end of log
            logs = BP_Log.query.filter(BP_Log.date >= request.form['start-date']).all()
            sys, dia, pulse = compute_averages(logs)
            return render_template('index.html', title=title, logs=logs, sys=sys, dia=dia, pulse=pulse)
        elif request.form['start-date'] and request.form['end-date']:
            logs = BP_Log.query.filter(BP_Log.date.between(request.form['start-date'], request.form['end-date'])).all()
            sys, dia, pulse = compute_averages(logs)
            return render_template('index.html', title=title, logs=logs, sys=sys, dia=dia, pulse=pulse)
        return render_template('index.html', title=title, logs=logs, avgs=avgs)
    else:
        return redirect(url_for('home'))

@app.route('/logs/new', methods=['GET','POST'])
def newLog():
    if request.method == 'GET':
        return render_template('new.html', title=title)
    if request.method == 'POST':
        # Validate user input
        if request.form['date'] == "" or request.form['time'] == "" or request.form['SYS'] == "" or \
            request.form['DIA'] == "" or request.form['Pulse'] == "":
            flash("All fields must have data")
            return render_template('new.html',date=request.form['date'], time=request.form['time'], \
                    sys=request.form['SYS'], dia=request.form['DIA'], pulse=request.form['Pulse'], title=title)
        try:
            sys = int(request.form['SYS'])
            dia = int(request.form['DIA'])
            pulse = int(request.form['Pulse'])
        except ValueError:
            flash("SYS, DIA and Pulse must be integers")
            # Render instead of redirect so as to preserve prior user input
            return render_template('new.html',date=request.form['date'], time=request.form['time'], \
                    sys=request.form['SYS'], dia=request.form['DIA'], pulse=request.form['Pulse'], title=title)
        # Add log to table
        newLog = BP_Log(request.form['date'], request.form['time'], sys, dia, pulse)
        db.session.add(newLog)
        db.session.commit()
        flash("BP log Added")
        return redirect(url_for('home'))

# DELETE log
@app.route('/logs/delete/<int:id>')
def delete_log(id):
    # Backup the database before delete
    shutil.copyfile("data/health_stats.db", "data/health_stats.bkup")
    # find and delete BP log
    me = BP_Log.query.filter_by(id=id).first()
    db.session.delete(me)
    db.session.commit()
    flash("Log deleted after database backed up")
    return redirect('/logs')

if __name__ == '__main__':
    app.run(debug=True)