//from https://www.w3schools.com/js/js_cookies.asp
export function setCookie(cname : string, cvalue : any, exdays=1) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    let expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}
export function getCookie(cname : string) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
}
export function checkCookie(cname : string) {
    let username = getCookie(cname);
    if (username != "") {
        return true;
    } else {
        return false;
    }
}
export function deleteCookie(key : string){
    if(checkCookie(key)){
        setCookie(key, "", 0);
    }
}