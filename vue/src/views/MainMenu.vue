<script setup lang="ts">
import { RouterLink } from 'vue-router'
import {onMounted} from "vue"

/*
function populateBackground(background : HTMLElement, el : HTMLElement, num : number){
  for(var x = 0; x < num; x++){
    let newNode = el.cloneNode();
    background.appendChild(newNode);
  }
}
function setupBackground(){
  let background:HTMLElement|null = document.getElementById("background");
  if(background != null){
    let el:HTMLElement|null = background.children[0] as HTMLElement|null;
    if(el != null){
      background.innerHTML = '';
      populateBackground(background, el, 100);
    }
  }
}
*/
onMounted(() => {
  //setupBackground();
})


</script>

<template>
  <div id="background" class="background">
    <div class="grid-div"></div>
  </div>
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
          <!--RouterLink will not actually load the data sent by the server directly-->
          <a href="/root">
            <i class="fa-solid fa-bug-slash"></i>
            <div class="tooltip no-edge">Digital Repository (DEBUG)</div>
          </a>
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
    height: 100%;
}
hr{
    position: relative;
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
    z-index: 2;
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
    width: calc(var(--item-size) + 10px);
    transform: translateY(calc((var(--item-size) / 2) + 50% - 15px));
}

.background{
  height: 100%;
  width: 100%;
  position: absolute;
  display: grid;
  grid-template-columns: [column-1] 10vw [column-2] 10vw [column-3] 10vw [column-4] 10vw [column-5] 10vw [column-6] 10vw [column-7] 10vw [column-8] 10vw [column-9] 10vw [column-10] 10vw [column-end];
  grid-template-rows: [row-1] 10vh [row-2] 10vh [row-3] 10vh [row-4] 10vh [row-5] 10vh [row-6] 10vh [row-7] 10vh [row-8] 10vh [row-9] 10vh [row-10] 10vh [row-end];

}

.grid-div{
  width: 100%;
  height: 100%;
  z-index: 1;
  transition: background-color 3s linear, box-shadow 3s linear;
}
.grid-div:hover{
 
  box-shadow: 0 0 50px 100px var(--color-pallette-darker) inset;
  transition: background-color -0.25s 2s linear, box-shadow  -0.25s 2s linear;
}

</style>
