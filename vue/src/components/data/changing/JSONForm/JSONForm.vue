<script setup lang="ts">
import { ref, onUnmounted, onMounted, defineComponent, useSlots, type Slot, type RendererElement, type RendererNode, type VNode} from 'vue';
import { computed } from '@vue/reactivity';
import {populate} from "@/assets/js/lib"
//import {defineDataStore} from "@/stores/DataStore"
import { stringifyExpression } from '@vue/compiler-core';
import JSONFormElement from './JSONFormElement.vue';

//TODO
let props = defineProps({
  postUrl: {
    type: String, 
    required: true,
  },
  value:{
    type: String,
    required: false,
    default: "Submit",
  },
  onSend:{
    type: Function,
    required: false,
    default: (success:boolean, message:string) => {},
  }
});

const slots = useSlots();
const childs = slots.default ? slots.default() : null;


//TODO get correct data (getData() will not be executed)
function submit(){
  var xhttp = new XMLHttpRequest();
  var jsonData:any = {}

  if(childs != null){
    for(var x = 0; x < childs.length; x++){
      if(childs[x].type == JSONFormElement){
        var p = childs[x].props;
        if(p != null){
          var data = p["data"];
          let keys:[] = p["keys"];

          var recursiveHelperJsonData = jsonData;
          for(var y = 0; y < keys.length; y++){
            if(recursiveHelperJsonData[keys[y]] == undefined)
              recursiveHelperJsonData[keys[y]] = {};
            recursiveHelperJsonData = recursiveHelperJsonData[keys[y]];
          }
          if(data instanceof Function)
            data = data();
          recursiveHelperJsonData[keys[keys.length - 1]] = data;
        }
      }
    }
  }
  let json:string = JSON.stringify(jsonData);

  xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if(this.status == 200) {
                var r = JSON.parse(this.responseText);
                props.onSend(!r['error']['set'], r['error']['message']);
            }
            else{
                props.onSend(false, "Status " + this.status + ": " + this.statusText);
            }
        }
    };

    xhttp.open("POST", props.postUrl, true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    //console.log(jsonData);
    xhttp.send(json);

}

</script>

<template>
  <table>
    <thead></thead>
    <tbody>
      <tr v-for="child in childs">
        <component :is="child"/>
      </tr>
    </tbody>
  </table>
  <input type="button" :value=props.value @click=submit />
</template>

<style scoped>

</style>@/stores/DataStore