import time
import threading

#returns total time slept
def WakeableSleep(cancellationToken, totalSleepingTime, maximumSleepingTime = 5):
    #type: (threading.Event, float, float) -> float
    totalStartTime = time.time()
    t = totalStartTime

    while totalSleepingTime > maximumSleepingTime and not cancellationToken.is_set():
        time.sleep(maximumSleepingTime)
        timeNeeded = time.time() - t
        t = time.time()
        totalSleepingTime = totalSleepingTime - timeNeeded

    if totalSleepingTime > 0 and not cancellationToken.is_set():
        time.sleep(totalSleepingTime)
    return time.time() - totalStartTime
