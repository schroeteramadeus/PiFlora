import time
import threading

#returns total time slept
def WakeableSleep(cancellationToken : threading.Event, totalSleepingTime : float, maximumSleepingCycleTime : float = 5) -> float:
    startTime : float = time.time()
    currentTime : float = startTime

    while totalSleepingTime > maximumSleepingCycleTime and not cancellationToken.is_set():
        time.sleep(maximumSleepingCycleTime)
        timeNeeded = time.time() - currentTime
        currentTime = time.time()
        totalSleepingTime = totalSleepingTime - timeNeeded

    if totalSleepingTime > 0 and not cancellationToken.is_set():
        time.sleep(totalSleepingTime)
    return time.time() - startTime
