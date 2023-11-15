import { ref, computed, type Ref } from 'vue'
import { defineStore } from 'pinia'

export const useConfigStore = defineStore("config", () => {

    const rootDirectory = "/root"

    const systemConfig = {
        serviceUrl: rootDirectory + "/system",
        logUrl: rootDirectory + "/system/logs",
    }
    const plantManagerConfig = {
        serviceUrl: rootDirectory + "/plantmanagerservice",
        statusUrl: rootDirectory + "/plantmanagerservice/status",
        switchUrl: rootDirectory + "/plantmanagerservice/switch",
        getPlantUrl: rootDirectory + "/plantmanagerservice/plants",
        changePlantUrl: rootDirectory + "/plantmanagerservice/plants/change",
        addPlantUrl: rootDirectory + "/plantmanagerservice/plants/add",
        plantNameFilterParam: "filter",
        plantManagerBluetoothFilter: "[Ff]lower[ ]*[Cc]are",
        plantIdParameter: "plant",
    }
    const pythonTypes = {
        waterPump : {
            gpio: "GPIOPump",
        },
        plantSensor : {
            miFlora: "MiFloraPlantSensor",
        },
    }
    const bluetoothConfig = {
        serviceUrl: rootDirectory + "/bluetoothservice",
        statusUrl: rootDirectory + "/bluetoothservice/status",
        switchUrl: rootDirectory + "/bluetoothservice/switch",
        allDevicesUrl: rootDirectory + "/bluetoothservice/devices",
    }

    const gpioConfig = {
        serviceUrl: rootDirectory + "/gpioservice",
        allGpiosUrl: rootDirectory + "/gpioservice/gpios/all",
        availableGpiosUrl: rootDirectory + "/gpioservice/gpios/available",
    }

    return {
        rootDirectory,
        systemConfig,
        pythonTypes,
        plantManagerConfig,
        gpioConfig,
        bluetoothConfig
    }
});