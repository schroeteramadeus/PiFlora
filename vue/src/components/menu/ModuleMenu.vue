<script setup lang="ts">
//TODO modularize buttons and status

let props = defineProps({
  title: {
    //TODO
    //type: RouteLocationRaw, 
    type: String,
    required: true,
  },
})

</script>

<template>
  <div class="menu">
    <nav class="top maxWidth">
      <ul>
        <slot name="item"></slot>
      </ul>
    </nav>
    <ul class="bottom maxWidth">
      <slot name="widgets"></slot>
    </ul>
  </div>
  <div class="content">
    <div class="title center">
        <h1>{{ title }}</h1>
    </div>
    <div class="data" id="dataFrame">
      <slot name="default"></slot>
    </div>
  </div>
</template>

<style scoped>
  
</style>
