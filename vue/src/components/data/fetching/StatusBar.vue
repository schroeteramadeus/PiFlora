<script setup lang="ts">
import { defineStatusStore,  } from '@/stores/StatusStore'
import {StatusVars} from "@/data/StatusVars"
import { ref, onUnmounted, onMounted } from 'vue';
import { computed } from '@vue/reactivity';


let props = defineProps({
  faIconClass: {
    type: String, 
    required: false, 
    default: "",
  },
  url: {
    type: String, 
    required: true,
  },
  updateTime: {
    type: Number, 
    required: false,
    default: 5000,
  },
})

let statusStore = defineStatusStore(props.url).get();

let fullPollStatus = computed(() => StatusVars.getFullPollStatus(statusStore.status.pollStatus, statusStore.status.debug))
let pollText = computed(() => StatusVars.getText(statusStore.status.pollStatus, statusStore.status.debug))

function updateFunc(){
    statusStore.update();
}

onUnmounted(() => {
  //TODO check if no other interval was set
  statusStore.clearUpdateInterval();
})
onMounted(() => {
  statusStore.setUpdateInterval(updateFunc, props.updateTime);
})
</script>

<template>
  <!-- Access the state directly from the store -->
  <i v-if="faIconClass != ''" :class=faIconClass></i>
  <span :data-poll-status=fullPollStatus>
    {{pollText}}
  </span>
</template>

<style scoped>
span {
    display: block;
}
</style>