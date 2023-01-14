HOST = "http://localhost:8080"
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

function changeView(iFrame, url){
    iFrame.src = url;
}

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

function populate(body, row, data, prefix, newDisplay){
    //TODO: check if rows are outdated (rather than killing everything)
    //delete last rows
    body.innerHTML = ""
    //create new rows
    for(x = 0; x < data.length; x++){
        var newTableRow = row.cloneNode(true)
        newTableRow.id = prefix + "_" + x

        populateDataRow(newTableRow, data[x], prefix);
        newTableRow.style.display = newDisplay
        body.appendChild(newTableRow)
    }
}

function populateDataRow(tableRow, dataDictionary, prefix = ""){
    var keys = Object.keys(dataDictionary)
    //console.log(keys);
    for(var x = 0; x < keys.length; x++){
        var data = dataDictionary[keys[x]];    
        //console.log(keys[x] + " | " + data);
        //data == dictionary
        if (data.constructor == Object) {
            populateDataRow(tableRow, data, prefix + "_" + keys[x]);
        }else{
            //console.log("populate: " + prefix + "_" + keys[x] + " with " + data);
            if (tableRow.getAttribute("data-poll") == prefix + "_" + keys[x]){
                tableRow.innerHTML = data
            }else{
                var element = tableRow.querySelector("*[data-poll=" + prefix + "_" + keys[x] + "]");
                if(element != null){
                    //TODO add support for more than one element
                    console.log("populate: " + prefix + "_" + keys[x] + " with " + data);
                    /*for(var y = 0; y < elements.length; y++){
                        console.log("populate: " + prefix + "_" + keys[x] + " with " + data);
                        element.innerHTML = data;
                    }*/
                    if(element.dataset.pollPopulate == null || element.dataset.pollPopulate == "" || element.dataset.pollPopulate == "data"){
                        element.dataset.pollData = data;
                    }else if(element.dataset.pollPopulate == "innerHTML"){
                        element.innerHTML = data;
                    }else if(element.dataset.pollPopulate = "value"){
                        element.value = data;
                    }else{
                        console.error("could not populate " + element.dataset.pollPopulate + " of " + element.dataset.poll); 
                    }
                }
            }
        }
    }
    //console.log(tableRow);
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

    var plant = plantName;

    xhttp.open("POST", HOST + PLANTMANAGERSERVICEPATH + "/plants/change?plant=" + plant, true);
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

    var plant = plantName;

    xhttp.open("POST", HOST + PLANTMANAGERSERVICEPATH + "/plants/delete?plant=" + plant, true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    //console.log(JSON.stringify(data));
    xhttp.send(JSON.stringify(data));
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

function getURIParameters(){
    return new URLSearchParams(window.location.search);
}

//from https://www.w3schools.com/js/js_cookies.asp
function setCookie(cname, cvalue, exdays=1) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    let expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}
function getCookie(cname) {
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
function checkCookie(cname) {
    let username = getCookie(cname);
    if (username != "") {
        return true;
    } else {
        return false;
    }
}
function deleteCookie(key){
    if(checkCookie(key)){
        setCookie(key, "", 0);
    }
}

function excecuteOnceAfter(func, timer){
    var n = setInterval(fadeOut, timer);
    function fadeOut(){
        func();
        clearInterval(n);
    }
}
function updateSelect(select, property){
    select.style.color = window.getComputedStyle(select.options[select.selectedIndex]).getPropertyValue(property);
}
function selectValue(select, value){
    success = false;
    for(var x = 0; x < select.options.length; x++){
        if(select.options[x].value == value){
            select.selectedIndex = x;
            success = true;
            break;
        }
    }
    return success;
}
function switchDisplay(el1, el2){
    display = el1.style.display;
    el1.style.display = el2.style.display;
    el2.style.display = display;
}