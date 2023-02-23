<script setup lang="ts">
import { defineStatusStore,  } from '@/stores/StatusStore'
import {StatusVars} from "@/data/StatusVars"
import { ref, onUnmounted, onMounted } from 'vue';
import { computed } from '@vue/reactivity';


let props = defineProps({
  statusUrl: {
    type: String, 
    required: true,
  },
  switchUrl: {
    type: String, 
    required: true,
  },
})

let statusStore = defineStatusStore(props.statusUrl).get();

function onStart(){
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        //TODO handle error
        //__bluetoothManagerOnStatusReady(el,this.responseText);
        statusStore.update();
      }
    };
    xhttp.open("GET", props.switchUrl + "?running=true", true);
    xhttp.send();
}
function onStop(){
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            //TODO handle error
            //__bluetoothManagerOnStatusReady(el,this.responseText);
            statusStore.update();
        }
    };
    xhttp.open("GET", props.switchUrl + "?running=false", true);
    xhttp.send();
}

</script>

<template>
  <div>
    <input type="button" @onclick=onStart value="Start"/>
    <input type="button" @onclick=onStop value="Stop"/>
  </div>
</template>