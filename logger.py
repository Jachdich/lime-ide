import datetime
def log(level, message):
    time = datetime.datetime.now().strftime("%d/%m %H:%M:%S")
    print(formstrings[level].format(time=time, msg=message))

formstrings = {
 "debug":   "[{time}] [ DEBUG ]: {msg}",
 "info":    "[{time}] [ INFO  ]: {msg}",
 "warning": "[{time}] [ WARN  ]: {msg}",
 "error":   "[{time}] [ ERROR ]: {msg}",
 "fatal":   "[{time}] [ FATAL ]: {msg}",
}
