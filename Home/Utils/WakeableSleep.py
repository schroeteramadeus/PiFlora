import time
import threading

#returns total time slept
def WakeableSleep(cancellationToken, totalSleepingTime, maximumSleepingTime = 5):
    #type: (threading.Event, float, float) -> float
    t = time.time()

    while totalSleepingTime > maximumSleepingTime and not cancellationToken.is_set():
        time.sleep(maximumSleepingTime)
        timeNeeded = time.time() - t
        totalSleepingTime = totalSleepingTime - timeNeeded

    if totalSleepingTime > 0 and not cancellationToken.is_set():
        time.sleep(totalSleepingTime)
    return time.time() - t
