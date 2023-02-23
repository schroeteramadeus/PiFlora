<script setup lang="ts">
import LogBanner from '@/components/LogBanner.vue'
import { RouterLink, RouterView } from 'vue-router'
/*
import { useLogStore } from './stores/LogStore';
const logStore = useLogStore()

let num = 0;
setInterval(()=>{
    if(num % 2 == 0){
        logStore.logError("TEST ERROR", "ERROR 0815");
    }else{
        logStore.logSuccess("TEST SUCCESS");
    }
    num++;
}, 5000)
*/

</script>

<template>
  <LogBanner />
  <RouterView />
</template>

<style scoped>

</style>
