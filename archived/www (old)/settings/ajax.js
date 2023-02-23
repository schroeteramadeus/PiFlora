//load lib
//from https://stackoverflow.com/questions/950087/how-do-i-include-a-javascript-file-in-another-javascript-file
var libjs = document.querySelector("script[src='/lib.js']");
if(libjs == null){
    libjs = document.createElement('script');
    libjs.type = 'text/javascript';
    libjs.async = false;
    libjs.src = "/lib.js";
    document.head.appendChild(libjs);
    console.warn("For better performance load /lib.js before");
}else{
    libjs.async = false;
}
//use same server
HOST = ""

SYSTEMSERVICEPATH = "/root/system"

function updateLogs(body, row, prefix, newDisplay = "table-row", readyFunc = ()=>{}, async = true){
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            populate(body, row, JSON.parse(this.responseText)["logs"], prefix, newDisplay);
            readyFunc();
        }
    };
    //TODO use filter
    var filter = "_*";
    //TODO use level
    var level = "info"

    xhttp.open("GET", HOST + SYSTEMSERVICEPATH + "/logs?filter=" + filter + "&level=" + level, async);
    xhttp.send();
}