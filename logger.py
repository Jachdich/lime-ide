import datetime, constants, os

if not os.path.isdir(".logs"):
    os.mkdir(".logs")

DEBUG   = "debug"
INFO    = "info"
WARNING = "warning"
ERROR   = "error"
FATAL   = "fatal"
def log(level, message):
    time = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S.%f")
    text = formstrings[level].format(time=time, msg=message)
    print(text)
    with open(os.path.join(".logs", constants.current_logfile), "a") as f:
        f.write(text + "\n")

formstrings = {
 "debug":   "[{time}] [ DEBUG ]: {msg}",
 "info":    "[{time}] [ INFO  ]: {msg}",
 "warning": "[{time}] [ WARN  ]: {msg}",
 "error":   "[{time}] [ ERROR ]: {msg}",
 "fatal":   "[{time}] [ FATAL ]: {msg}",
}
