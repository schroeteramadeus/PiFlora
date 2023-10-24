<script setup lang="ts">
import StatusBar from '@/components/data/fetching/StatusBar.vue'
import { useConfigStore } from '@/stores/ConfigStore';
import PlantMenu from './PlantMenu.vue'
import DataTable from '@/components/data/fetching/table/DataTable.vue';
import DataTableColumn from '@/components/data/fetching/table/DataTableColumn.vue';

const configStore = useConfigStore();
const tableUrl = configStore.bluetoothConfig.allDevicesUrl + "?filter=" + configStore.plantManagerConfig.plantManagerBluetoothFilter;
</script>

<template>
    <PlantMenu>
        <!--TODO filter-->
        <DataTable :url=tableUrl>
            <DataTableColumn name="MAC" poll-path="mac"></DataTableColumn>
            <DataTableColumn name="Name" poll-path="name"></DataTableColumn>
        </DataTable>
        <!--TODO show if sensor is used-->
        <!--h1 class="center">Bluetooth status:<StatusBar :url=configStore.bluetoothConfig.statusUrl /></h1>
        <br />
        <div class="center">
            <input type="button" onclick="startBluetooth(document.getElementById('bluetoothStatus'))" value="Start"/>
            <input type="button" onclick="stopBluetooth(document.getElementById('bluetoothStatus'))" value="Stop"/>
        </div>
        <br />
        <h1>Available sensors</h1>
        <table id="sensorTable" class="maxWidth dataTable">
            <thead class="maxWidth">
                <tr>
                    <th>Mac</th>
                    <th>Name</th>
                </tr>
            </thead>
            <tbody id="sensorTable_body" class="maxWidth">
                <tr id="sensor" style="display:none;" data-poll-index="data_mac">
                    <td data-poll="data_mac" data-poll-populate="innerHTML">ERROR</td>
                    <td data-poll="data_name" data-poll-populate="innerHTML">ERROR</td>
                </tr>
            </tbody>
        </table-->
    </PlantMenu>
</template>
    