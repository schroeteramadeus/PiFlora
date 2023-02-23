<script setup lang="ts">
//TODO status widgets
import { RouterLink } from 'vue-router'
import StatusBar from "@/components/data/fetching/StatusBar.vue"

let props = defineProps({
  url: {
    //TODO
    //type: RouteLocationRaw, 
    type: String,
    required: true,
  },
  tooltip: {
    //TODO
    //type: RouteLocationRaw, 
    type: String,
    required: true,
  },
  faIconClass: {
    type: String, 
    required: false, 
    default: "",
  },
})
</script>

<template>
    <li>
      <table class="statusTable">
        <tbody>
          <tr>
            <td>
              <i :class=faIconClass></i>
            </td>
            <td>
              <StatusBar :url=url></StatusBar>
            </td>
            <td class="tooltip no-edge">
              {{ tooltip }}
            </td>
          </tr>
        </tbody>
      </table>
    </li>
</template>

<style scoped>
  
</style>
