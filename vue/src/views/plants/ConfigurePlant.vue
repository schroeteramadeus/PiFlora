<script setup lang="ts">
import StatusBar from '@/components/data/fetching/StatusBar.vue'
import { useConfigStore } from '@/stores/ConfigStore';
import PlantMenu from './PlantMenu.vue'
import { useLogStore } from '@/stores/LogStore';
import {excecuteOnceAfter, getURIParameters, selectValue, populateDataRow, updateSelect} from '@/assets/js/lib'
import router from '@/router/index'
import { onMounted, ref } from 'vue';
import { eventTargetToElement } from '@/assets/js/lib';
import JSONForm from '@/components/data/changing/JSONForm/JSONForm.vue'
import JSONFormElement from '@/components/data/changing/JSONForm/JSONFormElement.vue'
import { computed } from '@vue/reactivity';
import {defineDataStore} from "@/stores/DataStore"

const configStore = useConfigStore();
const logStore = useLogStore();
const plantStore = defineDataStore(configStore.plantManagerConfig.getPlantUrl).get();

const gpioPumpStore = defineDataStore(configStore.gpioConfig.allGpiosUrl).get();
const mifloraPlantSensorStore = defineDataStore(configStore.bluetoothConfig.allDevicesUrl + "?" + configStore.plantManagerConfig.plantNameFilterParam + "=" + configStore.plantManagerConfig.plantManagerBluetoothFilter).get();

//TODO load pumps and sensors 

const PLANTIDPARAM : string = configStore.plantManagerConfig.plantIdParameter
const postUrl = ref();
let showForm = ref(false);

let formInitialData = ref({
    configuration: {
        name: "",
        temperature: {
            max: 100,
            min: 50
        },
        moisture: {
            max: 100,
            min: 50
        },
        light: {
            max: 100,
            min: 50
        },
        conductivity: {
            max: 100,
            min: 50
        }
    },
    pump: {
        type: null,
        id: null,
    },
    sensor:{
        type: null,
        id: null
    }
});

function HTMLElementToInputElement(el : HTMLElement | null) : HTMLInputElement | null {
    if(el != null)
        return el as HTMLInputElement;
    else
        return null;
}
function updatePlant(dataElement : HTMLElement, plantName : string, readyFunc = (success : boolean, message : string) => {}) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if(this.status == 200){
                var r = JSON.parse(this.responseText);
                if(!r['error']['set']){
                    populateDataRow(dataElement, r["plants"][0]);
                }
                readyFunc(!r['error']['set'], r['error']['message']);
            }
            else{
                readyFunc(false, "");
            }
        }
    };
    var filter = "^" + plantName + "$";

    xhttp.open("GET", configStore.plantManagerConfig.getPlantUrl + "?" + configStore.plantManagerConfig.plantIdParameter + "=" + filter, true);
    xhttp.send();
}
function loadPlant(plantName : string){
    //TODO fix
    plantStore.update();
    var data = plantStore.data.data["plants"];

    var oldPlantData = data.find((dataRow : { [x: string]: any; }) => {
        return dataRow['configuration']['name'] == plantName;
    });
    formInitialData.value = {
        configuration: {
            name: oldPlantData['configuration']['name'],
            temperature: {
                max: oldPlantData['configuration']['temperature']['max'],
                min: oldPlantData['configuration']['temperature']['min']
            },
            moisture: {
                max: oldPlantData['configuration']['moisture']['max'],
                min: oldPlantData['configuration']['moisture']['min']
            },
            light: {
                max: oldPlantData['configuration']['light']['max'],
                min: oldPlantData['configuration']['light']['min']
            },
            conductivity: {
                max: oldPlantData['configuration']['conductivity']['max'],
                min: oldPlantData['configuration']['conductivity']['min']
            }
        },
        pump: {
            type: oldPlantData['pump']['type'],
            id: oldPlantData['pump']['id']
        },
        sensor:{
            type: oldPlantData['sensor']['type'],
            id: oldPlantData['sensor']['id']
        }
    };
    //TODO log on error and redirect, show table on success

    showTable();
    /*
            if(!success){
                logStore.logError("Loading Plant '" + plantName + "'", message)
                //console.log('Could not load plant data for: ' + OLDPLANTNAME);
                excecuteOnceAfter(() => router.replace("/plantmanager/plants"), 1000)
            }
            else{
                logStore.logSuccess("Loaded Plant '" + plantName + "'");
                showTable()
            }
        })
    }
   */
}

function showTable(){
    showForm.value = true;
}
function hideTable(){
    showForm.value = false;
}
/*
//TODO check data?
function createData(dataElement : HTMLElement){
    let pumpId = null;
    let pumpType = HTMLElementToInputElement(dataElement.querySelector('#pumpTypes'))?.value;

    if(pumpType == configStore.pythonTypes.waterPump.gpio){
        pumpId = HTMLElementToInputElement(dataElement.querySelector('#gpioPumps'))?.value;
    }

    let sensorId = null;
    let sensorType = HTMLElementToInputElement(dataElement.querySelector('#sensorTypes'))?.value;

    if(sensorType == configStore.pythonTypes.plantSensor.miFlora){
        sensorId = HTMLElementToInputElement(dataElement.querySelector('#miFloraPlantSensors'))?.value;
    }

    return {
        configuration: {
            name: HTMLElementToInputElement(dataElement.querySelector('#name'))?.value,
            temperature: {
                max: HTMLElementToInputElement(dataElement.querySelector('#temperatureMax'))?.value,
                min: HTMLElementToInputElement(dataElement.querySelector('#temperatureMin'))?.value,
            },
            moisture: {
                max: HTMLElementToInputElement(dataElement.querySelector('#moistureMax'))?.value,
                min: HTMLElementToInputElement(dataElement.querySelector('#moistureMin'))?.value,
            },
            light: {
                max: HTMLElementToInputElement(dataElement.querySelector('#lightMax'))?.value,
                min: HTMLElementToInputElement(dataElement.querySelector('#lightMin'))?.value,
            },
            conductivity: {
                max: HTMLElementToInputElement(dataElement.querySelector('#conductivityMax'))?.value,
                min: HTMLElementToInputElement(dataElement.querySelector('#conductivityMin'))?.value,
            },
        },
        pump: {
            id: pumpId,
            type: pumpType,
        },
        sensor: {
            id: sensorId,
            type: sensorType,
        }
    };
}
function createPlant(dataElement : HTMLElement, readyFunc = (success : boolean, message : string)=>{}){
    var xhttp = new XMLHttpRequest();

    let data = createData(dataElement);


    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if(this.status == 200) {
                var r = JSON.parse(this.responseText);
                readyFunc(!r['error']['set'], r['error']['message']);
            }
            else{
                readyFunc(false, "");
            }
        }
    };
    xhttp.open("POST", configStore.plantManagerConfig.addPlantUrl, true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    //console.log(JSON.stringify(data));
    xhttp.send(JSON.stringify(data));
}
//TODO optimize (only send data that changed)
function changePlant(dataElement : HTMLElement, oldPlantName : string, readyFunc = (success : boolean, message:string)=>{}){
    var xhttp = new XMLHttpRequest();

    let data = createData(dataElement);

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if(this.status == 200) {
                var r = JSON.parse(this.responseText);
                //console.log(r);
                readyFunc(!r['error']['set'], r['error']['message']);
            }
            else{
                readyFunc(false, "");
            }
        }
    };

    var plant = "^" + oldPlantName + "$";

    xhttp.open("POST", configStore.plantManagerConfig.changePlantUrl + "?" + configStore.plantManagerConfig.plantNameFilterParam + "=" + plant, true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    //console.log(JSON.stringify(data));
    xhttp.send(JSON.stringify(data));
}
function submit(){
    if(!submitted){
        var table = document.getElementById('dataTable');
        if(table != null){
            let newName = HTMLElementToInputElement(table.querySelector('[data-poll=plant_configuration_name]'))?.value;
            //table.style.display = 'none';
            hideTable()

            //TODO only excecute when the button is not pressed again
            if(oldPlantName == null){
                createPlant(table, (success : boolean, message : string)=>{
                    if(success){
                        logStore.logSuccess("Added Plant '" + newName + "'")
                        excecuteOnceAfter(()=> router.replace('/plantmanager/plants/configure'), 1000)
                    }else{
                        logStore.logError("Adding plant '" + newName + "'", message);
                        showTable()
                    }
                });
            }else{
                changePlant(table, oldPlantName, (success : boolean, message : string)=>{
                    if(success){
                        if(oldPlantName != newName)
                            logStore.logSuccess("Changed Plant '" + oldPlantName + "' to '" + newName + "'")
                        else
                            logStore.logSuccess("Changed Plant '" + oldPlantName + "'")
                        //OLDPLANTNAME = newName
                        excecuteOnceAfter(() => router.replace({path: '/plantmanager/plants/configure', query: {PLANTIDPARAM: newName}}), 1000)
                        //window.location = 'configurePlant.html?' + PLANTIDPARAM + '=' + newName;
                    }else{
                        logStore.logError("Changing plant '" + oldPlantName + "'", message);
                        showTable()
                    }
                });
            }
            submitted = true;
        }
        else
            logStore.logError("Changing plant","No data");
        }
}
*/
function getData(id : string){
    return (document.getElementById(id) as HTMLInputElement).value;
}

function onSubmit(success : boolean, errorMessage : string){
    if(success == true){
        //TODO determine if add or change
        logStore.logSuccess("Added plant \"" + getData('plant_name') + "\"");
        //TODO redirect?
    }else{
        logStore.logError("Could not add or change plant", errorMessage);
    }
}

onMounted(() => {
    let params = getURIParameters();
    let oldPlantName : string | null = params.get(PLANTIDPARAM);

    if(oldPlantName != null){      
        postUrl.value = configStore.plantManagerConfig.changePlantUrl + "?" + configStore.plantManagerConfig.plantNameFilterParam + "=" + oldPlantName;
        loadPlant(oldPlantName);
        
    }else{
        postUrl.value = configStore.plantManagerConfig.addPlantUrl;
        showTable();
    }
    gpioPumpStore.update();
    mifloraPlantSensorStore.update();
})

//TODO load sensors and pumps
</script>

<template>
    <PlantMenu>
        <h1>New Plant</h1>
        <br />
        <JSONForm :post-url=postUrl v-if="showForm" :on-send=onSubmit>
            <JSONFormElement :data="() => {return getData('plant_name');}" :keys="['configuration', 'name']">
                <label for="plant_name">Name</label>
                <input id="plant_name" placeholder="Enter name..." :value=formInitialData.configuration.name />
            </JSONFormElement>
            <JSONFormElement :data="() => {return {min: getData('plant_temperature_min'), max: getData('plant_temperature_max')};}" :keys="['configuration', 'temperature']">
                <label>Temperature Span</label>
                <input id="plant_temperature_min" :value=formInitialData.configuration.temperature.min />
                <input id="plant_temperature_max" :value=formInitialData.configuration.temperature.max />
            </JSONFormElement>
            <JSONFormElement :data="() => {return {min: getData('plant_moisture_min'), max: getData('plant_moisture_max')};}" :keys="['configuration', 'moisture']">
                <label>Moisture Span</label>
                <input id="plant_moisture_min" :value=formInitialData.configuration.moisture.min />
                <input id="plant_moisture_max" :value=formInitialData.configuration.moisture.max />
            </JSONFormElement>
            <JSONFormElement :data="() => {return {min: getData('plant_light_min'), max: getData('plant_light_max')};}" :keys="['configuration', 'light']">
                <label>Light Span</label>
                <input id="plant_light_min" :value=formInitialData.configuration.light.min />
                <input id="plant_light_max" :value=formInitialData.configuration.light.max />
            </JSONFormElement>
            <JSONFormElement :data="() => {return {min: getData('plant_conductivity_min'), max: getData('plant_conductivity_max')};}" :keys="['configuration', 'conductivity']">
                <label>Conductivity Span</label>
                <input id="plant_conductivity_min" :value=formInitialData.configuration.conductivity.min />
                <input id="plant_conductivity_max" :value=formInitialData.configuration.conductivity.max />
            </JSONFormElement>
            <JSONFormElement :data="() => {return {type: getData('sensorTypes'), id: getData('miFloraPlantSensors')};}" :keys="['sensor']">
                <label>Sensor</label>
                <select id="sensorTypes">
                    <!--TODO add other sensor type select and polling info-->
                    <option id="sensorTypeMiFloraPlantSensor" 
                        :value=configStore.pythonTypes.plantSensor.miFlora 
                        :selected="formInitialData.sensor.type == configStore.pythonTypes.plantSensor.miFlora">
                        MiFlora Plantsensor
                    </option>
                </select>
                <select id="miFloraPlantSensors" @change="event => updateSelect(eventTargetToElement(event.target) as HTMLSelectElement, 'color')">
                    <option v-for="mifloraSensor in mifloraPlantSensorStore.data.data['devices']" 
                        id="sensorOption" 
                        :value="mifloraSensor['mac']" 
                        :selected="formInitialData.sensor.id == mifloraSensor['mac']" >
                        {{mifloraSensor['name'] + " (" + mifloraSensor['mac'] + ")"}}
                    </option>
                </select>
            </JSONFormElement>
            <JSONFormElement :data="() => {return {type: getData('pumpTypes'), id: getData('gpioPumps')};}" :keys="['pump']">
                <label>Pump</label>
                <select id="pumpTypes">
                    <!--TODO add other sensor type select and polling info-->
                    <option :value=configStore.pythonTypes.waterPump.gpio 
                        :selected="formInitialData.pump.type == configStore.pythonTypes.waterPump.gpio">
                        GPIO Pump
                    </option>
                </select>
                <select id="gpioPumps" @change="event => updateSelect(eventTargetToElement(event.target) as HTMLSelectElement, 'color')">
                    <option v-for="gpioPump in gpioPumpStore.data.data['gpios']" 
                        :value="gpioPump['port']" 
                        :selected="formInitialData.pump.id == gpioPump['port']" >
                        {{"Port " + gpioPump['port']}}
                        </option>
                </select>
            </JSONFormElement>
        </JSONForm>
    </PlantMenu>
</template>
    
<style scoped>
    select, input, label{
        width: 100%;
    }
    label{
        margin-right: 5px;
    }

</style>