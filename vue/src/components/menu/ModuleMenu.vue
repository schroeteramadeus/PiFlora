<script setup lang="ts">
import { switchDisplay } from '@/assets/js/lib';
import { ref } from '@vue/reactivity';
import {useSessionStore} from "@/stores/SessionStore";

const sessionStore = useSessionStore();

let props = defineProps({
  title: {
    //TODO
    //type: RouteLocationRaw, 
    type: String,
    required: true,
  },
})

function collapseMenu(e : Event){
  sessionStore.showSideMenu = !sessionStore.showSideMenu
}
</script>

<template>
  <div class="maximized module-menu">
    <header class="max-width">
      <nav class="header-menu">
        <ul class="maximized">
          <li><RouterLink to="/"><i class="fa-solid fa-angles-left"></i></RouterLink></li>
          <li @click=collapseMenu >
            <a>
              <i :class="'fa-solid fa-angle-left ' + (sessionStore.showSideMenu ? '' : 'rotate-180')"></i>
            </a>
          </li>
        </ul>
      </nav>
      <div class="max-width center title">
          <h1>{{ title }}</h1>
      </div>
    </header>
    <main class="max-width">
      <div :class="'max-height side-menu ' + (sessionStore.showSideMenu ? '' : 'menu-collapse')">
        <nav class="top max-width">
          <ul>
            <slot name="item"></slot>
          </ul>
        </nav>
        <ul class="bottom max-width">
          <slot name="widgets"></slot>
        </ul>
      </div>
      <div :class="'max-height content ' + (sessionStore.showSideMenu ? '' : 'content-unfold')" >
        <slot name="default"></slot>
      </div>
    </main>
  </div>
</template>

<style scoped>
@import url("@/assets/css/base.css");
.module-menu{
  --title-height: 30px;
  --menu-width: 100px;
}
nav{
  position: relative;
}
header{
  position: absolute;
  height: var(--title-height);
  z-index: 998;
  display: flex;
}
main{
  position: absolute;
  top: var(--title-height);
  height: calc(100% - var(--title-height));
  display: flex;
}
.header-menu{
    background-color: var(--color-pallette-darkest);
    width: var(--menu-width);
    height: 100%;
}
.header-menu ul{
  padding: 5px;
}
.header-menu ul li{
  display: inline-block;
  width: auto;
}
.header-menu ul li:last-child{
  float:right;
}
.side-menu{
    background-color: var(--color-pallette-darkest);
    border-right: 1px solid var(--color-pallette-darker);
    width: var(--menu-width);
    z-index: 998;
    transition: width 1s;
}
.side-menu ul{
  width: var(--menu-width);
}
.title{
    background-color: var(--color-pallette-darkest);
    height: var(--title-height);
    width: calc(100% - var(--menu-width));
}
.content{
    background-color: var(--color-pallette-medium-dark);
    width: calc(100% - var(--menu-width));
    z-index: 1;
    padding: 5px;
    transition: width 1s;
}

.menu-collapse{
  width: 0px;
}
.side-menu ul{
  transition: transform 1s;
}
.menu-collapse ul{
  transform: translateX(-100%);
}
.content-unfold{
  width: 100%;
}
.rotate-180{
  transform: rotate(180deg);
}

.fa-angle-left{
  transition: transform 1s;
}
</style>
