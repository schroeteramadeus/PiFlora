<script setup lang="ts">
import { useConfigStore } from '@/stores/ConfigStore';
import SettingsMenu from './SettingsMenu.vue';
import DataTable from '@/components/data/fetching/table/DataTable.vue';
import DataTableColumn from '@/components/data/fetching/table/DataTableColumn.vue';

const configStore = useConfigStore();
const filter = "_*";
const level = "info"
const tableUrl =configStore.systemConfig.logUrl + "?filter=" + filter + "&level=" + level


</script>

<template>
    <SettingsMenu>
        <DataTable :url=tableUrl >
            <DataTableColumn name="Level" poll-path="level"></DataTableColumn>
            <DataTableColumn name="Time" poll-path="time"></DataTableColumn>
            <DataTableColumn name="Logger" poll-path="logger"></DataTableColumn>
            <DataTableColumn name="Line" poll-path="line"></DataTableColumn>
            <DataTableColumn name="Message" poll-path="message"></DataTableColumn>
        </DataTable>
    </SettingsMenu>
</template>
    