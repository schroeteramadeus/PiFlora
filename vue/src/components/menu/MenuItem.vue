<script setup lang="ts">
import { RouterLink, type RouteLocationRaw } from 'vue-router'

let props = defineProps({
  url: {
    //TODO
    //type: RouteLocationRaw, 
    type: String,
    required: true,
  },
})
</script>

<template>
    <li class="max-width center">
        <RouterLink :to=url>
            <slot name="default"></slot>
        </RouterLink>
    </li>
</template>

<style scoped>
@import url("@/assets/css/base.css");
  li{
      height: var(--button-height);
      border-bottom: 1px solid var(--color-pallette-darker);
      display: block;
  }
  li:first-child{
    border-top: 1px solid var(--color-pallette-darker);
  }
  li:hover{
      background-color: var(--color-pallette-dark);
      cursor: pointer;
  }
  li:active{
      background-color: var(--color-pallette-medium);
  }

  a {
    width: 100%;
    height: 100%;
  }
</style>
