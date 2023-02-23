import {Status} from "@/stores/StatusStore"

export class StatusVars{
    static readonly POLLSTATUSTEXTACTIVE = "Active"
    static readonly POLLSTATUSTEXTDEBUG = "Debug"
    static readonly POLLSTATUSTEXTINACTIVE = "Inactive"
    static readonly POLLSTATUSTEXTERROR = "Error"
    static readonly POLLSTATUSTEXTPOLLING = "Polling..."
  
    static readonly POLLSTATUSDEBUG = "debug"
    static readonly POLLSTATUSACTIVE = "active"
    static readonly POLLSTATUSINACTIVE = "inactive"
    static readonly POLLSTATUSERROR = "error"
    static readonly POLLSTATUSPOLLING = "polling"
  
    static getText(pollStatus : number, debug: boolean) : string {
      var statusText = StatusVars.POLLSTATUSTEXTERROR
  
      if(pollStatus == Status.POLLSTATUSACTIVE){
        statusText = StatusVars.POLLSTATUSTEXTACTIVE
      }else if(pollStatus == Status.POLLSTATUSINACTIVE){
        statusText = StatusVars.POLLSTATUSTEXTINACTIVE
      }else if(pollStatus == Status.POLLSTATUSERROR){
        statusText = StatusVars.POLLSTATUSTEXTERROR
      }else if(pollStatus == Status.POLLSTATUSPOLLING){
        statusText = StatusVars.POLLSTATUSTEXTPOLLING
      }
  
      return statusText
    }
  
    static getFullPollStatus(pollStatus : number, debug: boolean) : string{
      var fullStatus = StatusVars.POLLSTATUSTEXTERROR
  
      if(pollStatus == Status.POLLSTATUSACTIVE){
        fullStatus = StatusVars.POLLSTATUSACTIVE
      }else if(pollStatus == Status.POLLSTATUSINACTIVE){
        fullStatus = StatusVars.POLLSTATUSINACTIVE
      }else if(pollStatus == Status.POLLSTATUSERROR){
        fullStatus = StatusVars.POLLSTATUSERROR
      }else if(pollStatus == Status.POLLSTATUSPOLLING){
        fullStatus = StatusVars.POLLSTATUSPOLLING
      }
      if(debug){
        fullStatus += " " + StatusVars.POLLSTATUSDEBUG
      }
  
      return fullStatus
    }
  }