<script setup lang="ts">
import SettingsMenu from './SettingsMenu.vue'
import DataTable from '@/components/data/fetching/table/DataTable.vue';
import DataTableColumn from '@/components/data/fetching/table/DataTableColumn.vue';
import { useLogStore } from '@/stores/LogStore';

const logStore = useLogStore();

</script>

<template>
    <SettingsMenu>
        <table>
            <thead>
                <tr>
                    <td>Message</td>
                </tr>
            </thead>
            <tbody>
                <tr v-for="log in logStore.log">
                    <td>{{ log }}</td>
                </tr>
            </tbody>
        </table>
        <!--TODO-->
    </SettingsMenu>
</template>
    