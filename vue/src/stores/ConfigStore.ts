import { ref, computed, type Ref } from 'vue'
import { defineStore } from 'pinia'


//TODO
export const useConfigStore = defineStore("config", () => {

    const rootDirectory = "/root"

    const plantManagerConfig = {
        serviceUrl: rootDirectory + "/plantmanagerservice",
        statusUrl: rootDirectory + "/plantmanagerservice/status",
        switchUrl: rootDirectory + "/plantmanagerservice/switch",
    }
    const bluetoothConfig = {
        serviceUrl: rootDirectory + "/bluetoothservice",
        statusUrl: rootDirectory + "/bluetoothservice/status",
        switchUrl: rootDirectory + "/bluetoothservice/switch",
    }

    return {
        rootDirectory,
        plantManagerConfig,
        bluetoothConfig
    }
});