<script setup lang="ts">
import { ref, onUnmounted, onMounted, defineComponent, useSlots} from 'vue';
import { computed } from '@vue/reactivity';
import {populate} from "@/assets/js/lib"
import {defineDataStore} from "@/stores/DataStore"

let props = defineProps({
  name: {
    type: String, 
    required: true,
  },
  
});

let childCount = ref(0);

const slots = useSlots();
const columns = slots.default ? slots.default() : null;

if(columns != null){
  childCount.value = columns.length;
}

</script>


<template>
  <!--TODO-->
  <tr>
    <th :colspan=childCount>{{ name }}</th>
  </tr>
    <slot name="default"></slot>
</template>

<style scoped>

</style>@/stores/DataStore