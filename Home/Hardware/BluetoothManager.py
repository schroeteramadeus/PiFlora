import subprocess
import time
import re
import threading
import queue
import sys
import logging
from sys import platform

from ..Utils.WakeableSleep import WakeableSleep
#"Singleton"

_logger = logging.getLogger(__name__)
debugMode = False
debugDeviceData = [{
    "mac":"DE:BU:G1:7a:8c",
    "name": "Flower Care"
    },{
    "mac":"DE:BU:G4:18:8d",
    "name": "Flower Care"
    }
]


if  "linux" not in platform:
    _logger.warning("Running Bluetoothmanager in debug mode")
    debugMode = True

def IsDebugMode():
    global debugMode
    return debugMode

def SetDebugMode(value: bool):
    global debugMode
    debugMode = value

class BluetoothManager:
    __startedInDebugMode = False
    __availableDevices = [] #type: list[dict[str,str]] #name and mac
    __availableDevicesLock = threading.Lock()
    __running = False
    __deviceFetchTask = None #type: threading.Thread
    __deviceFetchTaskCancellationToken = None #type:threading.Event

    def IsRunning() -> bool:
        #type: () -> bool
        return BluetoothManager.__running

    def IsDebug() -> bool:
        global debugMode
        #type: () -> bool
        return (debugMode and not BluetoothManager.IsRunning()) or BluetoothManager.__startedInDebugMode

    def Start():
        if not BluetoothManager.IsRunning():
            _logger.info("Bluetoothservice starting...")
            debug = debugMode #threadsafety (hopefully)
            if not debug:
                BluetoothManager.__deviceFetchTaskCancellationToken = threading.Event()
                BluetoothManager.__deviceFetchTask = threading.Thread(target=BluetoothManager.__fetchScanData, args=[BluetoothManager.__deviceFetchTaskCancellationToken, 10])
                BluetoothManager.__deviceFetchTask.start()
            
            BluetoothManager.__startedInDebugMode = debug
            BluetoothManager.__running = True
            _logger.debug("Bluetoothservice is now running")

    def Stop():
        if BluetoothManager.IsRunning():
            _logger.info("Bluetoothservice stopping...")
            if not BluetoothManager.__startedInDebugMode:
                if BluetoothManager.__deviceFetchTask != None:
                    _logger.debug("Stopping fetch task...")
                    BluetoothManager.__deviceFetchTaskCancellationToken.set()
                    BluetoothManager.__deviceFetchTask.join()
                _logger.debug("Cleanup...")
                BluetoothManager.__deviceFetchTaskCancellationToken = None
                BluetoothManager.__deviceFetchTask = None
            BluetoothManager.__startedInDebugMode = False
            BluetoothManager.__running = False
            _logger.debug("Bluetoothservice has now stopped")

    def GetAvailableDevices():
        #type: () -> list[dict[str,str]]
        devices = [] #type: list[dict[str,str]]
        if not BluetoothManager.IsDebug():
            with BluetoothManager.__availableDevicesLock:
                devices = BluetoothManager.__availableDevices
        else:
            devices = debugDeviceData
        return devices

    def GetFilteredAvailableDevices(filterNameMask):
        #type: () -> list[dict[str,str]]
        output = []#type: list[dict[str,str]]
        devices = BluetoothManager.GetAvailableDevices()

        for x in range(len(devices)):
            if re.match(filterNameMask, devices[x]["name"]):
                output.append(devices[x])
        return output

    def __fetchScanData(cancellationToken : threading.Event, scanningTime : float):
        _logger.info("Fetching task started...")

        while True:
            if cancellationToken.is_set():
                break
            newAvailableDevices = [] #type: list[dict[str,str]]
            deviceScanTask = None #type:subprocess.Popen
            _logger.info("Starting new bluetooth scan...")
            while deviceScanTask == None:
                deviceScanTask = subprocess.Popen("sudo timeout -s INT {}s hcitool lescan".format(scanningTime), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
                time.sleep(5)
                if deviceScanTask.poll() != None:
                    deviceScanTask.kill()
                    deviceScanTask.wait()
                    deviceScanTask.stderr.flush()
                    error = deviceScanTask.stderr.read()
                    if bool(error):
                        print(error.rstrip("\n"))
                        _logger.debug("Bluetooth currently not available, retrying...")
                        deviceScanTask = None
            _logger.debug("Scanning for devices...")
            deviceScanTask.wait(scanningTime)
            _logger.debug("Scanned devices")
            if cancellationToken.is_set():
                break
            deviceScanTask.stdout.flush()
            deviceScanTask.stderr.flush()
            lines = deviceScanTask.stdout.readlines()
            error = deviceScanTask.stderr.read()
            if not bool(error):
                _logger.debug("Scan successful")

                _logger.info("Start fetching data...")
                for line in lines:
                    line = line.rstrip("\n")
                    _logger.debug("Bluetooth manager read: " + line)

                    #if(re.match("\[sudo\]", line)):
                    #    print("Bluetooth manager requests password...")
                    #    deviceScanTask.stdin.writelines([input("Password for bluetoothservice needed: ")])
                    #    deviceScanTask.stdin.flush()
                    if re.match("([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2} *)", line):
                        _logger.debug("Bluetooth manager: Device found")
                        args = line.split(" ")
                        mac = args[0]
                        name = ""
                        for y in range(1, len(args)):
                            name += args[y] + " "
                        name = name.strip()
                        device = {
                            'mac' : mac,
                            'name' : name,
                        }
                        if device not in newAvailableDevices:
                            newAvailableDevices.append(device)
                        #TODO maybe delete older not found devices?
                        _logger.debug("Device " + name + " [" + mac + "] added")
                    else:
                        _logger.debug("Bluetooth manager: Line ignored")
                    if cancellationToken.is_set():
                        break
                
                with BluetoothManager.__availableDevicesLock:
                    BluetoothManager.__availableDevices = newAvailableDevices

                if not cancellationToken.is_set():
                    _logger.debug("Bluetooth manager: Sleep")
                    #no new data
                    WakeableSleep(cancellationToken, 60)
                else:
                    break
            else:
                _logger.warning("Bluetooth manager encountered error: " + error)
                _logger.warning("Bluetooth manager tries restarting...")
                time.sleep(5)
        if cancellationToken.is_set():
            _logger.debug("Fetching task ended")
        else:
            _logger.warning("Fetching task ended unexpectedly")

                # BluetoothManager.Stop()
                # deviceScanTask.kill()
                # deviceScanTask.wait()
                # deviceScanTask.stderr.flush()
                # error = deviceScanTask.stderr.read()
                # print("Bluetoothmanager: Error")
                # raise ChildProcessError(error)