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

</style>@/stores/DataStore