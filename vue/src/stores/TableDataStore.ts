import { ref, computed, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { urlToName } from '@/assets/js/lib'

export function defineTableDataStore(dataURL : string){
  return {
    get:getOrCreateStore(urlToName(dataURL), dataURL)
  }
}

export class Data{
  errorMessage:string;
  errorSet:boolean;
  data: any;

  constructor(data:{ [x: string]: any; }, errorMessage:string) {
    this.data = data;

    if (errorMessage == null || errorMessage == ""){
      this.errorMessage = "";
      this.errorSet = false;
    }else{
      this.errorMessage = errorMessage;
      this.errorSet = true;
    }
  }
}

function getOrCreateStore(name : string, dataURL : string){
  return defineStore(name, () => {
    const initialized = ref(false);
    const counter = ref(0);
    const data = ref(new Data({}, ""));
    const interval:Ref<null | number> = ref(null);

    function update(showPolling:boolean = false) {
      if(showPolling){
        data.value = new Data({}, "");
      }
      var xhttp = new XMLHttpRequest();
  
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
          if(this.status == 200){
            try{
                var response = JSON.parse(this.responseText);
    
                if(response["error"]["set"] == false){
                    delete response["error"];
                    data.value = new Data(response, "");
                }
                else{
                    data.value = new Data({}, response["error"]["message"]);
                }
            }
            catch{
                data.value = new Data({}, "No valid JSON");
            }
          }else{
            data.value = new Data({}, "Unknown error");
          }
          initialized.value = true
        }
      };
      xhttp.open("GET", dataURL, false);
      xhttp.send();
    }

    function setUpdateInterval(func:TimerHandler, time : number){
      if(interval.value == null){
        interval.value = setInterval(func, time);
      }
      counter.value++;
    }
    function clearUpdateInterval(){
      if(interval.value != null && counter.value == 1){
        clearInterval(interval.value);
        interval.value = null;
      }
      counter.value--;
    }
    return {
      initialized,
      data,
      update,
      setUpdateInterval,
      clearUpdateInterval
    }
  });
}