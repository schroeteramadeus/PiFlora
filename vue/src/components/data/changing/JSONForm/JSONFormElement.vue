<script setup lang="ts">
import { ref, onUnmounted, onMounted, defineComponent, useSlots, type Slot, type RendererElement, type RendererNode, type VNode} from 'vue';
import { computed } from '@vue/reactivity';
import {populate} from "@/assets/js/lib"
import {defineTableDataStore} from "@/stores/TableDataStore"

//TODO
let props = defineProps({
    data: {
        type: [Function, Object],
        required: true,
    },
    keys: {
        type: Array<string>,
        required: true,
    }
});

const slots = useSlots();
const childs = slots.default ? slots.default() : null;

</script>

<template>
    <td v-for="child in childs">
        <component :is="child"/>
    </td>
</template>

<style scoped>
</style>