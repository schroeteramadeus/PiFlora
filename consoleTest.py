import Home.Hardware.BluetoothManager as BM
import Home.Hardware.Sensors.Plant.MiFloraPlantSensor as MiFloraPS
import Home.Hardware.Actors.Water.GPIOPump as PUMP
import Home.Plants.Plant as P
import Home.Plants.PlantConfiguration as PC
import Home.Utils.ValueSpan as VS
import Home.Plants.PlantManager as PM
from Home.Hardware.GPIOManager import GPIOManager, GPIOTypes

import time
import re
import logging
import sys
import ConsoleFilter as CF
import Home.Hardware.Sensors.Water.AlwaysActiveWaterSensor as AAWS

plantManager = None #type:PM.PlantManager
error = None #type: Exception

try:
    BM.BluetoothManager.Start()
    while len(BM.BluetoothManager.GetAvailableDevices()) == 0:
        print("scanning for devices...")
        for x in BM.BluetoothManager.GetAvailableDevices():
            print("device: " + x["name"] + " | " + x["mac"])
        time.sleep(10) #let bluetooth catch up
    BM.BluetoothManager.Stop()
    print("Detected Sensors:")
    plants = []
    sensors = BM.BluetoothManager.GetFilteredAvailableDevices("[Ff]lower [Cc]are")
    for x in range(len(sensors)):
        sensor = sensors[x]
        print(sensor["name"] + " | " + sensor["mac"])
        plantSensor = MiFloraPS.MiFloraPlantSensor(sensor["mac"])
        plantConfiguration = PC.PlantConfiguration(
            name="Plant",
            temperatureSpan=VS.ValueSpan(20.0, 25.0),
            moistureSpan=VS.ValueSpan(40, 70),
            conductivitySpan=VS.ValueSpan(40, 70),
            lightSpan=VS.ValueSpan(100, 500))
        plantPump = PUMP.GPIOPump(GPIOManager.GetFilteredAvailableGPIOs(GPIOTypes.STANDARDINOUT)[0])
        plant = P.Plant(plantSensor=plantSensor,plantConfiguration=plantConfiguration,hardware={
            P.Plant.HARDWARE_PUMP:plantPump,
        })
        plants.append(plant)

    print()
    print("Initializing plant manager...")
    plantManager = PM.PlantManager(AAWS.AlwaysActiveWaterSensor())
    plantManager.PollInterval = 15
    plantManager.CriticalInterval = 30
    #TODO also use FileHandler (but on module level logger!!!)
    #handler = logging.StreamHandler(sys.stdout)
    #handler.setLevel(logging.DEBUG)
    #handler.addFilter(CF.ConsoleFilter())
    #handler.setFormatter(logging.Formatter(fmt="[%(levelname)-5.5s]  %(message)s"))
    #handler.setFormatter(logging.Formatter(fmt="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"))
    #plantManager.Logger.addHandler(handler)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    handler.addFilter(CF.ConsoleFilter())

    root.addHandler(handler)


    print("Success")
    print()
    for plant in plants:
        plantManager.Add(plant)
    print("added plants")
    plantManager.Start()
    while True:
        time.sleep(15)
    
    #message = input()
    #while(message != "exit"):
        #do something
    #    message = input()
    plantManager.Stop()
except Exception as e:
    error = e
except KeyboardInterrupt as interrupt:
    error = interrupt
finally:
    if plantManager != None and plantManager.IsRunning:
        plantManager.Stop()
    if BM.BluetoothManager.IsRunning:
        BM.BluetoothManager.Stop()
    if error != None:
        raise error



# from miflora import miflora_scanner, miflora_poller
# from btlewrap import GatttoolBackend as BluetoothBackend, PygattBackend, BluepyBackend
# from miflora.miflora_poller import (
#     MI_BATTERY,
#     MI_CONDUCTIVITY,
#     MI_LIGHT,
#     MI_MOISTURE,
#     MI_TEMPERATURE,
# )
# import subprocess
# import time

# def getAllDevices(timeout:int = 10):
#     output = []
#     p = subprocess.Popen("sudo timeout -s INT {}s hcitool lescan".format(timeout), stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True, shell=True)
#     p.wait()
#     processOutput = str(p.communicate())
#     if(processOutput.find("error") == -1 and processOutput.find("fail") == -1):
#         processOutput = processOutput.split("\\n")
#         #first and last no devicesDEBUG
#         for x in range(1, len(processOutput) - 1):
#             args = processOutput[x].split(" ")
#             mac = args[0]
#             name = ""
#             for y in range(1, len(args)):
#                 name += args[y] + " "
#             name = name.strip()
#             argDict = {
#                 'mac' : mac,
#                 'name' : name,
#             }
#             output.append(argDict)
#     else:
#         raise ChildProcessError(processOutput)
#     return output

# def filterDevices(deviceList:list, filterNames:list):
#     output = []
#     for x in range(len(deviceList)):
#         for y in range(len(filterNames)):
#             if(deviceList[x]['name'].lower().replace(" ","").find(filterNames[y].lower().replace(" ", "")) != -1):
#                 output.append(deviceList[x])
#                 break
#     return output

# def getAllSensors(timeout:int = 10, filterNames:list = ["flower care"]):
#     #print("search for devices... ", end="", flush=True)
#     availableDevices = getAllDevices()
#     #print("Done", flush=True)

#     #print("filter for devices... ", end="", flush=True)
#     sensors = filterDevices(availableDevices, ["flower care"])
#     #print("Done", flush=True)
#     return sensors

# def pollSensor(mac, pollCount = 5):
#     currentTime = time.time();
#     poller = miflora_poller.MiFloraPoller(mac, BluetoothBackend)
#     output = {
#         'firmware': poller.firmware_version(),
#         'name': poller.name(),
#         'battery': poller.parameter_value(MI_BATTERY),
#         'temperature': 0.0,
#         'moisture': 0.0,
#         'light': 0.0,
#         'conductivity': 0.0,
#     }
#     for x in range(pollCount):
#         data = {
#             'temperature': float(poller.parameter_value(MI_TEMPERATURE) / pollCount),
#             'moisture': float(poller.parameter_value(MI_MOISTURE) / pollCount),
#             'light': float(poller.parameter_value(MI_LIGHT) / pollCount),
#             'conductivity': float(poller.parameter_value(MI_CONDUCTIVITY) / pollCount),
#         }
#         output['temperature'] += data['temperature']
#         output['moisture'] += data['moisture']
#         output['light'] += data['light']
#         output['conductivity'] += data['conductivity']
#         poller.clear_cache()
#         poller.clear_history()
#         if x < pollCount - 1:
#             time.sleep(10)
#     print("Sensor polled in: " + str(time.time() - currentTime) + "s")
#     return output
    

# sensors = getAllSensors()

# print("Available Sensors:")
# for device in sensors:
#     print("Mac: " + device['mac'] + ", Name: " + device['name'])

# for x in range(len(sensors)):
#     data = pollSensor(sensors[x]['mac'])
    
#     print("----------------------------------" + sensors[x]['name'] + "----------------------------------")

#     print("Firmware: {}".format(data['firmware']))
#     print("Temperature: {}".format(data['temperature']))
#     print("Moisture: {}".format(data['moisture']))
#     print("Light: {}".format(data['light']))
#     print("Conductivity: {}".format(data['conductivity']))
#     print("Battery: {}".format(data['battery']))