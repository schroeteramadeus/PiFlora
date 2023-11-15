<script setup lang="ts">
import StatusBar from '@/components/data/fetching/StatusBar.vue'
import PlantMenu from './PlantMenu.vue'
import router from '@/router/index'
import { useLogStore } from '@/stores/LogStore';
import {eventTargetToElement} from '@/assets/js/lib'
import { useConfigStore } from '@/stores/ConfigStore';
import StartStop from '@/components/data/changing/StartStop.vue';


const logStore = useLogStore();
const configStore = useConfigStore();
const PLANTIDPARAM = configStore.plantManagerConfig.plantIdParameter;


</script>

<template>
    <PlantMenu>
        <h1 class="center">Plant manager status:<StatusBar :url=configStore.plantManagerConfig.statusUrl /></h1>
        
        <br />
        <div class="center">
            <StartStop :switch-url=configStore.plantManagerConfig.switchUrl :status-url=configStore.plantManagerConfig.statusUrl />
        </div>
        <input type="button" @click="event => router.push('/plantmanager/plants/configure')" value="New plant"/>
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
                    <th>Light span</th>
                    <th>Moisture span</th>
                    <th>Conductvity span</th>
                    <th>Temperature span</th>
                </tr>
            </thead>
            <tbody id="setupTable_body" class="maxWidth">
                <tr id="plantConfig" style="display:none;" data-poll-index="data_configuration_name">
                    <td><span data-poll="data_configuration_name" data-poll-populate="innerHTML">ERROR</span></td>
                    <td><span data-poll="data_configuration_light_min" data-poll-populate="innerHTML">ERROR</span>-<span data-poll="data_configuration_light_max" data-poll-populate="innerHTML">ERROR</span></td>
                    <td><span data-poll="data_configuration_moisture_min" data-poll-populate="innerHTML">ERROR</span>-<span data-poll="data_configuration_moisture_max" data-poll-populate="innerHTML">ERROR</span></td>
                    <td><span data-poll="data_configuration_conductivity_min" data-poll-populate="innerHTML">ERROR</span>-<span data-poll="data_configuration_conductivity_max" data-poll-populate="innerHTML">ERROR</span></td>
                    <td><span data-poll="data_configuration_temperature_min" data-poll-populate="innerHTML">ERROR</span>-<span data-poll="data_configuration_temperature_max" data-poll-populate="innerHTML">ERROR</span></td>
                    <td data-poll="data_sensor_id" data-poll-populate="innerHTML">
                        ERROR
                    </td>
                    <td data-poll="data_pump_id" data-poll-populate="innerHTML">
                        ERROR
                    </td>
                    <td>
                        <a @click="event => router.push({path: '/plantmanager/plants/configure', query: {PLANTIDPARAM: eventTargetToElement(event.target)?.parentElement?.parentElement?.querySelector('[data-poll=data_configuration_name]')?.innerHTML}})" ><i class="fa-solid fa-gear"></i></a>
                        </td>
                    <td>
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
                            deletePlant(this.parentElement.parentElement.querySelector('[data-poll=data_configuration_name]').innerHTML);
                            //TODO show success / delete plant?
                            var row = this.parentElement.parentElement;
                            row.remove();
                        " style="display:none;"><i class="fa-solid fa-trash-can-arrow-up"></i></a>
                    </td>
                </tr>
            </tbody>
        </table>
    </PlantMenu>
</template>
    