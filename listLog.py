import os, sys
from peewee import *

if len(sys.argv) ==3:
    startDate = sys.argv[1]
    endDate = sys.argv[2]
    print("This list is from {} to {}.". format(startDate, endDate))
elif len(sys.argv) == 2:
    startDate = sys.argv[1]
    endDate = None
    print("This list starts from {}.". format(startDate))
else:
    # Select all logs in table
    print('This list is of all logs')
    startDate = None

print("Date\t\t\tTime\t\tSYS\tDIA\tPULSE")
print("----\t\t\t----\t\t---\t---\t-----")

db = SqliteDatabase('data/health_stats.db')

class BaseModel(Model):
    class Meta:
        database = db

class bp_log(BaseModel):
    id = PrimaryKeyField()
    date = CharField()
    time = CharField()
    sys =  IntegerField()
    dia = IntegerField()
    pulse = IntegerField()

def output(logs, totlogs):
    ''' Accumulate totals and format output '''
    totsys = 0
    totdia = 0
    totpulse = 0
    for log in logs:
        totsys += log.sys
        totdia += log.dia
        totpulse += log.pulse
        out = '{}\t\t{}\t\t{}\t{}\t{}'.format(log.date, log.time, log.sys, log.dia, log.pulse)
        print(out)
    avg = '\nAverage: {}/{} {}'.format(round(totsys/totlogs), round(totdia/totlogs), round(totpulse/totlogs))
    print("\n", avg)

db.connect()

if not startDate:
    logs = bp_log.select()
    totlogs = len(logs)
    output(logs, totlogs)
elif startDate and not endDate:
    logs = bp_log.select().where(bp_log.date >= startDate)
    totlogs = len(logs)
    output(logs, totlogs)
elif startDate and endDate:
    logs = bp_log.select().where((bp_log.date >= startDate) & (bp_log.date <= endDate))
    totlogs = len(logs)
    output(logs, totlogs)

db.close()



