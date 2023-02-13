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
BLUETOOTHSERVICEPATH = "/root/bluetoothservice"
PLANTMANAGERSERVICEPATH = "/root/plantmanagerservice"
GPIOMANAGERSERVICEPATH = "/root/gpioservice"

POLLSTATUSACTIVE = "active"
POLLSTATUSDEBUG = "debug"
POLLSTATUSINACTIVE = "inactive"
POLLSTATUSERROR = "error"
POLLSTATUSPOLLING = "polling"

POLLSTATUSTEXTACTIVE = "Active"
POLLSTATUSTEXTDEBUG = "Debug"
POLLSTATUSTEXTINACTIVE = "Inactive"
POLLSTATUSTEXTERROR = "Error"
POLLSTATUSTEXTPOLLING = "Polling..."

MIFLORAPLANTSENSORTYPE = "MiFloraPlantSensor"
GPIOPUMPTYPE = "GPIOPump"

function startBluetooth(el) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        __bluetoothManagerOnStatusReady(el,this.responseText);
      }
    };
    xhttp.open("GET", HOST + BLUETOOTHSERVICEPATH + "/switch?running=true", true);
    xhttp.send();
}

function stopBluetooth(el) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            __bluetoothManagerOnStatusReady(el,this.responseText);
        }
    };
    xhttp.open("GET", HOST + BLUETOOTHSERVICEPATH + "/switch?running=false", true);
    xhttp.send();
}

function checkBluetooth(el) {
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            __bluetoothManagerOnStatusReady(el,this.responseText);
        }
    };
    xhttp.open("GET", HOST + BLUETOOTHSERVICEPATH + "/status", true);
    xhttp.send();
}
function checkPlantmanager(el) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            __plantManagerOnStatusReady(el,this.responseText);
        }
    };
    xhttp.open("GET", HOST + PLANTMANAGERSERVICEPATH + "/status", true);
    xhttp.send();
}

function startPlantmanager(el) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            __plantManagerOnStatusReady(el,this.responseText);
        }
    };
    xhttp.open("GET", HOST + PLANTMANAGERSERVICEPATH + "/switch?running=true", true);
    xhttp.send();
}

function stopPlantmanager(el) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            __plantManagerOnStatusReady(el,this.responseText);
        }
    };
    xhttp.open("GET", HOST + PLANTMANAGERSERVICEPATH + "/switch?running=false", true);
    xhttp.send();
}
function updateSetup(body, row, prefix, newDisplay = "table-row", readyFunc = ()=>{}) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            //console.log(JSON.parse(this.responseText)["plants"]);
            populate(body, row, JSON.parse(this.responseText)["plants"], prefix, newDisplay);
            readyFunc();
        }
    };
    xhttp.open("GET", HOST + PLANTMANAGERSERVICEPATH + "/plants", true);
    xhttp.send();
}

function updateSensors(body, row, prefix, newDisplay = "table-row", readyFunc = ()=>{}, async = true) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            populate(body, row, JSON.parse(this.responseText)["devices"], prefix, newDisplay);
            readyFunc();
        }
    };
    var filter = "[Ff]lower[ ]*[Cc]are";

    xhttp.open("GET", HOST + BLUETOOTHSERVICEPATH + "/devices?filter=" + filter, async);
    xhttp.send();
}

function updateGPIOs(body, row, prefix, newDisplay = "table-row", readyFunc = ()=>{}, async = true) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            populate(body, row, JSON.parse(this.responseText)["gpios"], prefix, newDisplay);
            readyFunc();
        }
    };
    var filter = "standardinout";

    xhttp.open("GET", HOST + GPIOMANAGERSERVICEPATH + "/gpios/all?filter=" + filter, async);
    xhttp.send();
}


function updatePlant(dataElement, plantName, prefix, readyFunc = (success)=>{}){
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if(this.status == 200){
                var r = JSON.parse(this.responseText);
                if(!r['error']['set']){
                    populateDataRow(dataElement, r["plants"][0], prefix);
                }
                readyFunc(!r['error']['set']);
            }
            else{
                readyFunc(false);
            }
        }
    };
    var filter = "^" + plantName + "$";

    xhttp.open("GET", HOST + PLANTMANAGERSERVICEPATH + "/plants?filter=" + filter, true);
    xhttp.send();
}
//TODO check data?
function createPlant(dataElement, readyFunc = (success)=>{}){
    var xhttp = new XMLHttpRequest();

    pumpId = null;
    pumpType = dataElement.querySelector('#pumpTypes').value;

    if(pumpType == GPIOPUMPTYPE){
        pumpId = dataElement.querySelector('#gpioPumps').value;
    }

    sensorId = null;
    sensorType = dataElement.querySelector('#sensorTypes').value;

    if(sensorType == MIFLORAPLANTSENSORTYPE){
        sensorId = dataElement.querySelector('#miFloraPlantSensors').value;
    }

    data = {
        configuration: {
            name: dataElement.querySelector('#name').value,
            temperature: {
                max: dataElement.querySelector('#temperatureMax').value,
                min: dataElement.querySelector('#temperatureMin').value,
            },
            moisture: {
                max: dataElement.querySelector('#moistureMax').value,
                min: dataElement.querySelector('#moistureMin').value,
            },
            light: {
                max: dataElement.querySelector('#lightMax').value,
                min: dataElement.querySelector('#lightMin').value,
            },
            conductivity: {
                max: dataElement.querySelector('#conductivityMax').value,
                min: dataElement.querySelector('#conductivityMin').value,
            },
        },
        pump: {
            id: pumpId,
            type: pumpType,
        },
        sensor: {
            id: sensorId,
            type: sensorType,
        }
    };


    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if(this.status == 200) {
                var r = JSON.parse(this.responseText);
                readyFunc(!r['error']['set']);
            }
            else{
                readyFunc(false);
            }
        }
    };
    xhttp.open("POST", HOST + PLANTMANAGERSERVICEPATH + "/plants/add", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    //console.log(JSON.stringify(data));
    xhttp.send(JSON.stringify(data));
}
//TODO check data?
//TODO optimize (only send data that changed)
function changePlant(dataElement, plantName, readyFunc = (success)=>{}){
    var xhttp = new XMLHttpRequest();

    pumpId = null;
    pumpType = dataElement.querySelector('#pumpTypes').value;

    if(pumpType == GPIOPUMPTYPE){
        pumpId = dataElement.querySelector('#gpioPumps').value;
    }

    sensorId = null;
    sensorType = dataElement.querySelector('#sensorTypes').value;

    if(sensorType == MIFLORAPLANTSENSORTYPE){
        sensorId = dataElement.querySelector('#miFloraPlantSensors').value;
    }

    data = {
        configuration: {
            name: dataElement.querySelector('#name').value,
            temperature: {
                max: dataElement.querySelector('#temperatureMax').value,
                min: dataElement.querySelector('#temperatureMin').value,
            },
            moisture: {
                max: dataElement.querySelector('#moistureMax').value,
                min: dataElement.querySelector('#moistureMin').value,
            },
            light: {
                max: dataElement.querySelector('#lightMax').value,
                min: dataElement.querySelector('#lightMin').value,
            },
            conductivity: {
                max: dataElement.querySelector('#conductivityMax').value,
                min: dataElement.querySelector('#conductivityMin').value,
            },
        },
        pump: {
            id:pumpId,
            type:pumpType,
        },
        sensor: {
            id:dataElement.querySelector('#miFloraPlantSensors').value,
            type:dataElement.querySelector('#sensorType').value,
        }
    };

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if(this.status == 200) {
                var r = JSON.parse(this.responseText);
                //console.log(r);
                readyFunc(!r['error']['set']);
            }
            else{
                readyFunc(false);
            }
        }
    };

    var plant = "^" + plantName + "$";

    xhttp.open("POST", HOST + PLANTMANAGERSERVICEPATH + "/plants/change?filter=" + plant, true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    //console.log(JSON.stringify(data));
    xhttp.send(JSON.stringify(data));
}
function deletePlant(plantName, readyFunc = (success)=>{}){
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if(this.status == 200) {
                var r = JSON.parse(this.responseText);
                //console.log(r);
                readyFunc(!r['error']['set']);
            }
            else{
                readyFunc(false);
            }
        }
    };

    var plant = "^" + plantName + "$";

    xhttp.open("POST", HOST + PLANTMANAGERSERVICEPATH + "/plants/delete?filter=" + plant, true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    //console.log(JSON.stringify(data));
    xhttp.send();
}

function __plantManagerOnStatusReady(el, response){
    var r = JSON.parse(response);
    if(el != null){
        if(r["running"] == true){
            el.innerHTML = POLLSTATUSTEXTACTIVE
            el.dataset.pollStatus = POLLSTATUSACTIVE
            
            if(r["debug"] == true)
                el.dataset.pollStatus += " " + POLLSTATUSDEBUG
            else if(r["debug"] != false)
                el.dataset.pollStatus = " " + POLLSTATUSERROR
        }
        else if(r["running"] == false){
            el.innerHTML = POLLSTATUSTEXTINACTIVE
            el.dataset.pollStatus = POLLSTATUSINACTIVE
            
            if(r["debug"] == true)
                el.dataset.pollStatus += " " + POLLSTATUSDEBUG
            else if(r["debug"] != false)
                el.dataset.pollStatus = " " + POLLSTATUSERROR
        }
        else{
            el.innerHTML = POLLSTATUSTEXTERROR
            el.dataset.pollStatus = POLLSTATUSERROR
        }
        if(r["error"]["set"])
            el.dataset.pollStatus = " " + POLLSTATUSERROR

    }
}
function __bluetoothManagerOnStatusReady(el, response){
    var r = JSON.parse(response);
    if(el != null){
        if(r["running"] == true){
            el.innerHTML = POLLSTATUSTEXTACTIVE
            el.dataset.pollStatus = POLLSTATUSACTIVE

            if(r["debug"] == true)
                el.dataset.pollStatus += " " + POLLSTATUSDEBUG
            else if(r["debug"] != false)
                el.dataset.pollStatus = " " + POLLSTATUSERROR
        }
        else if(r["running"] == false){
            el.innerHTML = POLLSTATUSTEXTINACTIVE
            el.dataset.pollStatus = POLLSTATUSINACTIVE

            if(r["debug"] == true)
                el.dataset.pollStatus += " " + POLLSTATUSDEBUG
            else if(r["debug"] != false)
                el.dataset.pollStatus = " " + POLLSTATUSERROR
        }
        else{
            el.innerHTML = POLLSTATUSTEXTERROR
            el.dataset.pollStatus = POLLSTATUSERROR
        }
        if(r["error"]["set"])
            el.dataset.pollStatus = " " + POLLSTATUSERROR
    }
}