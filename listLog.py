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

class BaseMoel(Model):
    class Meta:
        database = db

class bp_log(BaseModel):
    id = PrimaryKeyField()
    date = CharField()
    time = CharField()
    sys =  IntegerField()
    dia = IntegerField()
    pulse = IntegerField()

db.connect()

if not startDate:
    for log in bp_log.select():
        out = '{}\t\t{}\t\t{}\t{}\t{}'.format(log.date, log.time, log.sys, log.dia, log.pulse)
        print(out)
elif startDate and not endDate:
    for log in bp_log.select().where(bp_log.date >= startDate):
        out = '{}\t\t{}\t\t{}\t{}\t{}'.format(log.date, log.time, log.sys, log.dia, log.pulse)
        print(out)
elif startDate and endDate:
    for log in bp_log.select().where((bp_log.date >= startDate) & (bp_log.date <= endDate)):
        out = '{}\t\t{}\t\t{}\t{}\t{}'.format(log.date, log.time, log.sys, log.dia, log.pulse)
        print(out)


db.close()



