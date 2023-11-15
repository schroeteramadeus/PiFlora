import { ref, computed, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { urlToName } from '@/assets/js/lib'

export function defineStatusStore(statusURL : string){
  return {
    get:getOrCreateStore(urlToName(statusURL), statusURL)
  }
}

export class Status{
  static readonly POLLSTATUSPOLLING = 0
  static readonly POLLSTATUSACTIVE = 1
  static readonly POLLSTATUSINACTIVE = 2
  static readonly POLLSTATUSERROR = 3

  pollStatus:number;
  errorMessage:string;
  errorSet:boolean;
  debug:boolean;

  constructor(pollStatus:number, debug:boolean, errorMessage:string) {
    this.pollStatus = pollStatus;
    this.debug = debug;
    if (errorMessage == null || errorMessage == ""){
      this.errorMessage = "";
      this.errorSet = false;
    }else{
      this.errorMessage = errorMessage;
      this.errorSet = true;
    }
  }
}

function getOrCreateStore(name : string, statusURL : string){
  return defineStore(name, () => {
    const initialized = ref(false)
    const counter = ref(0)
    const status = ref(new Status(Status.POLLSTATUSPOLLING, false, ""));
    const interval:Ref<null | number> = ref(null);

    function update(showPolling:boolean = false) {
      if(showPolling){
        status.value = new Status(Status.POLLSTATUSPOLLING, false, "")
      }
      var xhttp = new XMLHttpRequest();
  
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
          if(this.status == 200){
            try{
              var response = JSON.parse(this.responseText);

              if(response["error"]["set"] == false){
                if(response["running"] == true){
                  status.value = new Status(Status.POLLSTATUSACTIVE, response["debug"], "");
                }
                else {
                  status.value = new Status(Status.POLLSTATUSINACTIVE, response["debug"], "");
                }
              }
              else{
                status.value = new Status(Status.POLLSTATUSERROR, false, response["error"]["message"]);
              }
            }
            catch{
              status.value = new Status(Status.POLLSTATUSERROR, false, "No valid JSON");
            }
          }else{
            status.value = new Status(Status.POLLSTATUSERROR, false, "Unknown error");
          }
          initialized.value = true
        }
      };
      xhttp.open("GET", statusURL, false);
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
      status,
      update,
      setUpdateInterval,
      clearUpdateInterval
    }
  });
}