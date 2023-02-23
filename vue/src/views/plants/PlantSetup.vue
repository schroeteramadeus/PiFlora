<script setup lang="ts">
import StatusBar from '@/components/data/fetching/StatusBar.vue'
import { useConfigStore } from '@/stores/ConfigStore';
import PlantMenu from './PlantMenu.vue'

const configStore = useConfigStore();
</script>

<template>
    <PlantMenu>
        <h1 class="center">Plant manager status:<StatusBar :url=configStore.plantManagerConfig.statusUrl /></h1>
        
        <br />
        <div class="center">
            <input type="button" onclick="startPlantmanager(document.getElementById('plantmanagerStatus'))" value="Start"/>
            <input type="button" onclick="stopPlantmanager(document.getElementById('plantmanagerStatus'))" value="Stop"/>
        </div>
        <input type="button" onclick="window.location='configurePlant.html'" value="New plant"/>
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
                        <a onclick="window.location = 'configurePlant.html?plant=' + this.parentElement.parentElement.querySelector('[data-poll=data_configuration_name]').innerHTML;"><i class="fa-solid fa-gear"></i></a>
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
    