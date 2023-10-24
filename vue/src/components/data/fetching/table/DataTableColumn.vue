<script setup lang="ts">
import { ref, onUnmounted, onMounted, defineComponent, useSlots} from 'vue';
import { computed } from '@vue/reactivity';
import {populate} from "@/assets/js/lib"
import {defineTableDataStore} from "@/stores/TableDataStore"

let props = defineProps({
  name: {
    type: String, 
    required: true,
  },
  pollPath: {
    type: String, 
    required: true,
  }
});
</script>

<template>
    <th>{{ name }}</th>
</template>

<style scoped>

</style>