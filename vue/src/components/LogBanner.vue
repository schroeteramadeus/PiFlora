//TODO
<script setup lang="ts">
//TODO use log store
import { useLogStore } from '@/stores/LogStore';
import { computed, ref } from '@vue/reactivity';
import { RouterLink, type RouteLocationRaw } from 'vue-router'
import {excecuteOnceAfter} from "@/assets/js/lib"
import { onMounted, onUnmounted } from 'vue';

let props = defineProps({
    showTime: {
        type: Number, 
        required: false, 
        default: 1000,
    },
})

const logStore = useLogStore()


const fadeOut = ref("")
const popIn = ref("")
const color = ref("")
const text = ref("")

function onNewError(){
    popIn.value = "";
    fadeOut.value = "";
    text.value = logStore.lastErrorAction + ", " + logStore.lastError
    color.value = "red"
    popIn.value = "pop-in"
    excecuteOnceAfter(fadeOutFunc, props.showTime + 500);
}
function onNewSuccess(){
    popIn.value = "";
    fadeOut.value = "";
    text.value = logStore.lastSuccessAction
    color.value = "green"
    popIn.value = "pop-in"
    excecuteOnceAfter(fadeOutFunc, props.showTime + 500);
}

function fadeOutFunc(){
    fadeOut.value = "fade-out"
    popIn.value = ""
}

onMounted(() => {
    logStore.bindOnSuccess(onNewSuccess);
    logStore.bindOnError(onNewError);
})

onUnmounted(() => {
    logStore.unbindOnSuccess(onNewSuccess);
    logStore.unbindOnError(onNewError);
})

</script>

<template>
    <div :class='"log-banner center " + color + " " + fadeOut + " " +  popIn'>
        <p>{{ text }}</p>
    </div>
</template>

<style scoped>
    @import url("../assets/css/base.css");
    .log-banner{
        left:50%;
        transform: translate(-50%, -100%);
        position: fixed;
        width: 30%;
        min-width: 250px;
        height: 75px;
        overflow: hidden;
        opacity: 1;
        z-index: 999;
        color: var(--text-color-light);
        transition: transform .5s, opacity .5s linear;
    }
    .log-banner p{
        position: relative;
        height: auto;
        width: auto;
        margin: 5px;
        top: 50%;
        transform: translate(0%, calc(-50% - 5px));
    }
    .fade-out{
        opacity: 0;
    }
    .pop-in{
        transform: translate(-50%,10%);
    }
    .green {
        background-color: var(--color-pallette-positive);
    }
    .red {
        background-color: var(--color-pallette-negative);
    }
</style>