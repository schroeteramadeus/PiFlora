<script setup lang="ts">
import { ref, onUnmounted, onMounted, defineComponent, useSlots, type Slot, type RendererElement, type RendererNode, type VNode} from 'vue';
import { computed } from '@vue/reactivity';
import {populate} from "@/assets/js/lib"
//import {defineDataStore} from "@/stores/TableDataStore"

//TODO
let props = defineProps({
  data: {
    type: [], 
    required: false,
    default: ["Error, no data"],
  },
});
/*
let dataTableStore = defineTableDataStore(props.url).get();

let name = dataTableStore.$id;

let defaultRow:HTMLTableRowElement|null = null;

function onUpdate(){
    dataTableStore.update();
    populateTable()
}

onMounted(()=>{
    populateTable();
    onUpdate();
    dataTableStore.setUpdateInterval(onUpdate, props.updateTime);
})
onUnmounted(()=>{
    dataTableStore.clearUpdateInterval();
})
*/
</script>

<template>
    <!--select :name=name>
        <option v-for="x in props.data">Polling...</option>
    </select-->
</template>

<style scoped>

</style>@/stores/DataStore