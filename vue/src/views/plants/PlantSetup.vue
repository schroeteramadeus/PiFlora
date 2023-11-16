<script setup lang="ts">
import StatusBar from '@/components/data/fetching/StatusBar.vue'
import PlantMenu from './PlantMenu.vue'
import router from '@/router/index'
import { useLogStore } from '@/stores/LogStore';
import {eventTargetToElement} from '@/assets/js/lib'
import { useConfigStore } from '@/stores/ConfigStore';
import StartStop from '@/components/data/changing/StartStop.vue';
import { defineDataStore } from '@/stores/DataStore';
import { onMounted, onUnmounted } from 'vue';
import { switchDisplay } from '@/assets/js/lib';


const logStore = useLogStore();
const configStore = useConfigStore();

const plantStore = defineDataStore(configStore.plantManagerConfig.getPlantUrl).get();

const PLANTIDPARAM = configStore.plantManagerConfig.plantIdParameter;

const plantConfigureUrl = "/plantmanager/plants/configure";

//console.log(configStore.plantManagerConfig.getPlantUrl);
//console.log(plantStore.data.data);



onMounted(() => {
    plantStore.update();
    plantStore.setUpdateInterval(plantStore.update, 5000);
})
onUnmounted(()=>{
    plantStore.clearUpdateInterval();
})

</script>

<template>
    <PlantMenu>
        <h1 class="center">Plant manager status:<StatusBar :url=configStore.plantManagerConfig.statusUrl /></h1>
        
        <br />
        <div class="center">
            <StartStop :switch-url=configStore.plantManagerConfig.switchUrl :status-url=configStore.plantManagerConfig.statusUrl />
        </div>
        <input type="button" @click="event => router.push(plantConfigureUrl)" value="New plant"/>
        <br />

        <h1>Current setup</h1>
        
        <table id="setupTable" class="maxWidth dataTable">
            <thead class="maxWidth">
                <tr>
                    <th colspan="5">Plant</th>
                    <th rowspan="2">Sensor ID</th>
                    <th rowspan="2">Pump ID</th>
                    <th colspan="2" rowspan="2"></th>
                </tr>
                <tr>
                    <th>Name</th>
                    <th>Temperature span</th>
                    <th>Moisture span</th>
                    <th>Light span</th>
                    <th>Conductvity span</th>
                </tr>
            </thead>
            <tbody id="setupTable_body" class="maxWidth">
                <tr v-for="plant in plantStore.data.data['plants']" id="plantConfig">
                    <td><span>{{ plant['configuration']['name'] }}</span></td>                    
                    <td><span>{{ plant['configuration']['temperature']['min'] }}</span>-<span>{{ plant['configuration']['temperature']['max'] }}</span></td>
                    <td><span>{{ plant['configuration']['moisture']['min'] }}</span>-<span>{{ plant['configuration']['moisture']['max'] }}</span></td>
                    <td><span>{{ plant['configuration']['light']['min'] }}</span>-<span>{{ plant['configuration']['light']['max'] }}</span></td>
                    <td><span>{{ plant['configuration']['conductivity']['min'] }}</span>-<span>{{ plant['configuration']['conductivity']['max'] }}</span></td>
                    <td>
                        <!--TODO add type-->
                        {{ plant['sensor']['id'] }}
                    </td>
                    <td>
                        <!--TODO add type-->
                        {{ plant['pump']['id'] }}
                    </td>
                    <td>
                        <!--eventTargetToElement(event.target)?.parentElement?.parentElement?.querySelector('[data-poll=data_configuration_name]')?.innerHTML-->
                        <!--see https://stackoverflow.com/questions/10640159/key-for-javascript-dictionary-is-not-stored-as-value-but-as-variable-name-->
                        <a @click="event => router.push({path: plantConfigureUrl, query: {[PLANTIDPARAM]: plant['configuration']['name']}})" ><i class="fa-solid fa-gear"></i></a>
                        </td>
                    <td>
                        <!--TODO fix switchDisplay, deletePlant-->
                        <!--TODO create switch button / confirm button as modular component-->
                        <a id="trashButton" onclick="
                            var el = this;
                            var confirmEl = el.parentElement.querySelector('#trashButtonConfirm');

                            function reset(){
                                switchDisplay(el, confirmEl);
                                confirmEl.removeEventListener('mouseout', reset);
                            }
                            confirmEl.addEventListener('mouseout', reset);
                            switchDisplay(el, confirmEl); 
                        "><i class="fa-solid fa-trash-can"></i></a>

                        <a id="trashButtonConfirm" onclick="
                            deletePlant(plant['configuration']['name']);
                            //TODO show success / delete plant?
                            //var row = this.parentElement.parentElement;
                            //row.remove();
                        " style="display:none;"><i class="fa-solid fa-trash-can-arrow-up"></i></a>
                    </td>
                </tr>
            </tbody>
        </table>
    </PlantMenu>
</template>
    