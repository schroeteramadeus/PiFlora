import { computed, ref, watch, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { setCookie, checkCookie, deleteCookie, getCookie } from '@/assets/js/cookies';

//TODO implement login / logout
//NOTE: this storage will be persistent for one day
export const useSessionStore = defineStore("session", () => {

    const showSideMenu = ref(true);
    load(showSideMenu, "showSideMenu");
    setWatcher(showSideMenu, "showSideMenu", save);

    return {
        showSideMenu
    }
});

function load(variable: Ref<any>, name : string){
    if (checkCookie(name)){
        variable.value = JSON.parse(getCookie(name));
    }
}

function setWatcher(variable: Ref<any>, name : string, func : Function){
    watch(variable, (value) => {
        func(value, name);
    }, { deep: true });
}

function save(value: any, name : string){
    setCookie(name, JSON.stringify(value), 1);
}