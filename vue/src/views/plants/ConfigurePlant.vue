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

const configStore = useConfigStore();
const logStore = useLogStore()

//TODO load pumps and sensors 

const PLANTIDPARAM : string = configStore.plantManagerConfig.plantIdParameter
const postUrl = configStore.plantManagerConfig.addPlantUrl;

let showForm = ref(false);

let params = getURIParameters();

let oldPlantName : string | null = params.get(PLANTIDPARAM);

let submitted = false;


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
    var table = document.getElementById('dataTable');
    //logStore.log('Loading plant: ' + oldPlantName);

    if(table != null){
        updatePlant(table, plantName, (success : boolean, message : string)=>{
            if(success){
                var sensorTypesSelect = document.getElementById('sensorTypes') as HTMLSelectElement;
                var pumpTypesSelect = document.getElementById('pumpTypes') as HTMLSelectElement;
                var sensorType = HTMLElementToInputElement(document.getElementById('sensorType'))?.value;
                var pumpType = HTMLElementToInputElement(document.getElementById('pumpType'))?.value;

                success = selectValue(sensorTypesSelect, sensorType);
                if(success){
                    success = selectValue(pumpTypesSelect, pumpType);
                    if(success){
                        success = false;
                        if(sensorType == configStore.pythonTypes.plantSensor.miFlora){
                            success = selectValue(document.getElementById('miFloraPlantSensors') as HTMLSelectElement, HTMLElementToInputElement(document.getElementById('sensorId'))?.value);
                        }
                        if(success){
                            success = false;
                            if(pumpType == configStore.pythonTypes.waterPump.gpio){
                                success = selectValue(document.getElementById('gpioPumps') as HTMLSelectElement, HTMLElementToInputElement(document.getElementById('pumpId'))?.value);
                            }
                        }
                    }
                }
            }
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
    if(oldPlantName != null){
        loadPlant(oldPlantName);
    }else{
        showTable();
    }
})


//TODO load sensors and pumps
</script>

<template>
    <PlantMenu>
        <h1>New Plant</h1>
        <div style="display:hidden;">
            <span id="oldSensorID" style="display:hidden;" data-poll="plant_sensor_id" data-poll-populate="innerHTML"></span>
            <span id="oldSensorType" style="display:hidden;" data-poll="plant_sensor_type" data-poll-populate="innerHTML"></span>
            
            <span id="oldPumpID" style="display:hidden;" data-poll="plant_pump_id" data-poll-populate="innerHTML"></span>
            <span id="oldPumpType" style="display:hidden;" data-poll="plant_pump_type" data-poll-populate="innerHTML"></span>   
        </div>
        <br />
        <!--TODO-->
        <JSONForm :post-url=postUrl v-if="showForm" :on-send=onSubmit>
            <JSONFormElement :data="() => {return getData('plant_name');}" :keys="['configuration', 'name']">
                <label for="plant_name">Name</label>
                <input id="plant_name" placeholder="Enter name..." value="" />
            </JSONFormElement>
            <JSONFormElement :data="() => {return {min: getData('plant_temperature_min'), max: getData('plant_temperature_max')};}" :keys="['configuration', 'temperature']">
                <label>Temperature Span</label>
                <input id="plant_temperature_min" value="50" />
                <input id="plant_temperature_max" value="100" />
            </JSONFormElement>
            <JSONFormElement :data="() => {return {min: getData('plant_moisture_min'), max: getData('plant_moisture_max')};}" :keys="['configuration', 'moisture']">
                <label>Moisture Span</label>
                <input id="plant_moisture_min" value="50" />
                <input id="plant_moisture_max" value="100" />
            </JSONFormElement>
            <JSONFormElement :data="() => {return {min: getData('plant_light_min'), max: getData('plant_light_max')};}" :keys="['configuration', 'light']">
                <label>Light Span</label>
                <input id="plant_light_min" value="50" />
                <input id="plant_light_max" value="100" />
            </JSONFormElement>
            <JSONFormElement :data="() => {return {min: getData('plant_conductivity_min'), max: getData('plant_conductivity_max')};}" :keys="['configuration', 'conductivity']">
                <label>Conductivity Span</label>
                <input id="plant_conductivity_min" value="50" />
                <input id="plant_conductivity_max" value="100" />
            </JSONFormElement>
            <JSONFormElement :data="() => {return {type: getData('sensorTypes'), id: getData('miFloraPlantSensors')};}" :keys="['sensor']">
                <label>Sensor</label>
                <select id="sensorTypes">
                    <!--TODO add other sensor type select-->
                    <option id="sensorTypeMiFloraPlantSensor" value="MiFloraPlantSensor" selected="true">MiFlora Plantsensor</option>
                </select>
                <select id="miFloraPlantSensors" @change="event => updateSelect(eventTargetToElement(event.target) as HTMLSelectElement, 'color')">
                    <option id="sensorOption" style="display:none;" data-poll="data_mac">Polling...</option>
                </select>
            </JSONFormElement>
            <JSONFormElement :data="() => {return {type: getData('pumpTypes'), id: getData('gpioPumps')};}" :keys="['pump']">
                <label>Pump</label>
                <select id="pumpTypes">
                    <!--TODO add other sensor type select-->
                    <option value="GPIOPump" selected="true">GPIO Pump</option>
                </select>
                <select id="gpioPumps" @change="event => updateSelect(eventTargetToElement(event.target) as HTMLSelectElement, 'color')">
                    <option style="display:none;" data-poll="data_mac">Polling...</option>
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