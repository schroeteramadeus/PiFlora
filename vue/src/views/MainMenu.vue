<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <main>
      <nav>
        <!--other stuff-->
        <ul>
          <li>
            <RouterLink to="/plantmanager">
              <i class="fa-solid fa-seedling"></i>
              <div class="tooltip no-edge">Plant Manager</div>
            </RouterLink>
          </li>
      </ul>
      <hr />
      <!--internal stuff-->
      <ul>
        <li>
          <RouterLink to="/help">
            <i class="fa-solid fa-question"></i>
            <div class="tooltip no-edge">Help</div>
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/settings">
            <i class="fa-solid fa-gear"></i>
            <div class="tooltip no-edge">Settings</div>
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/root">
            <i class="fa-solid fa-bug-slash"></i>
            <div class="tooltip no-edge">Digital Repository (DEBUG)</div>
          </RouterLink>
        </li>
      </ul>
      </nav>
  </main>
</template>

<style scoped>
main {
    --item-size: 100px;
    --icon-size: calc(var(--item-size) * 0.5);
}
main {
    padding-left: 5%;
    padding-right: 5%;
    overflow: auto !important;
}
hr{
    border: 5px solid var(--color-pallette-darker);
    border-radius: 20px;
}
ul{
  display: flex;
  position: relative;
  margin-bottom: 50px;
  margin-top: 50px;
}
ul li{
    width: var(--item-size);
    height: var(--item-size);
    background-color: var(--color-pallette-darkest);
    margin: 3px;
    border-radius: 20px;
}
li a{
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}
li a i{
    font-size: var(--icon-size);
}
.tooltip{
    width: var(--item-size);
}
</style>
