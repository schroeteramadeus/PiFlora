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
    <li class="center">
        <RouterLink :to=url>
            <slot name="default"></slot>
        </RouterLink>
    </li>
</template>

<style scoped>
  a {
    width: 100%;
    height: 100%;
  }
</style>
