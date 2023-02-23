<script setup lang="ts">
import StatusBar from '@/components/data/fetching/StatusBar.vue'
import ModuleMenu from '@/components/menu/ModuleMenu.vue'
import MenuItem from '@/components/menu/MenuItem.vue'
import MenuWidget from '@/components/menu/MenuWidget.vue'
import { useConfigStore } from '@/stores/ConfigStore';

//TODO set route according to cookies
const configStore = useConfigStore();
</script>

<template>
    <ModuleMenu title="Plantmanager">
        <template v-slot:item>
            <!--TODO save router info on click and load after new menu button click-->
            <MenuItem url="/">Menu</MenuItem>
            <MenuItem url="/help/info">Info</MenuItem>
        </template>
        <slot name="default"></slot>
    </ModuleMenu>
</template>
    