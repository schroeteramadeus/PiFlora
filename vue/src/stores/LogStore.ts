import { ref, computed, type Ref } from 'vue'
import { defineStore } from 'pinia'
import {removeOnceFromArray} from "@/assets/js/lib"

export const useLogStore = defineStore("log", () => {
    const onErrorEvent:Ref<Function[]> = ref([]);
    const onSuccessEvent:Ref<Function[]> = ref([]);

    const log:Ref<string[]> = ref([])

    const lastError = ref("")
    const lastErrorAction = ref("")
    const lastErrorTime = ref(-1)

    const lastSuccessAction = ref("")
    const lastSuccessTime = ref(-1)
    
    function logError(actionMessage : string, errorMessage : string){
        lastErrorAction.value = actionMessage;
        lastError.value = errorMessage;
        lastErrorTime.value = Date.now();

        log.value.push("[" + getDateString(lastErrorTime.value) + "] Error on request: " + actionMessage + " - " + errorMessage);
        
        onErrorEvent.value.forEach((func)=>{
            func()
        });
    }
    function logSuccess(actionMessage : string){
        lastSuccessAction.value = actionMessage;
        lastSuccessTime.value = Date.now();
        
        log.value.push("[" + getDateString(lastErrorTime.value) + "] Success on request: " + actionMessage);
    
        onSuccessEvent.value.forEach((func)=>{
            func()
        });
    }

    function bindOnSuccess(func : Function){
        onSuccessEvent.value.push(func);
    }
    function unbindOnSuccess(func : Function){
        removeOnceFromArray(onSuccessEvent.value, func);
    }

    function bindOnError(func : Function){
        onErrorEvent.value.push(func);
    }
    function unbindOnError(func : Function){
        removeOnceFromArray(onErrorEvent.value, func);
    }

    return {
        lastError,
        lastErrorTime,
        lastErrorAction,

        lastSuccessAction,
        lastSuccessTime,

        logError,
        logSuccess,

        bindOnSuccess,
        unbindOnSuccess,
        bindOnError,
        unbindOnError,
    }
});

function getDateString(miliseconds : number) : string{
    return new Date(miliseconds).toUTCString()
}