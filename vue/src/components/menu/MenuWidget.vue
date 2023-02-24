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
      <table class="status-table">
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
.status-table {
    margin: 5px;
}
.status-table td:has(> i) {
    width: var(--status-icon-size);
    height: var(--status-icon-size);
    font-size: calc(var(--status-icon-size) * 0.9);
}
.status-table td:has(> *[data-poll-status]) {
    width: calc(var(--menu-width) - var(--status-icon-size));
    height: var(--status-icon-size);
    padding-left: 5px;
}
.status-table td > * {
    width: 100%;
    height: var(--status-icon-size);
}
.status-table .tooltip {
    transform: translate(0%, calc(-100% + var(--status-icon-size)));
}
  
</style>
