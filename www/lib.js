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

function changeView(iFrame, url){
    iFrame.src = url;
}
//data-poll-index = dataKey //unique identifier in order to find updated data
function populate(body, row, data, prefix, newDisplay){
    //delete last rows
    oldRows = body.children;
    for(x = 0; x < oldRows.length; x++){
        if (oldRows[x].dataset.pollIndex != null){
            var newTableRow = row.cloneNode(true)
            var index = -1
            var dictPath = oldRows[x].dataset.pollIndex.split("_").splice(1);

            for(y = 0; y < data.length; y++){
                var newData = data[y];
                
                while(dictPath.length > 0){
                    newData = newData[dictPath[0]];
                    dictPath = dictPath.splice(1);
                }
                var oldIndexElement = oldRows[x].querySelector("[data-poll='" + oldRows[x].dataset.pollIndex + "']");
                var oldDataPosition = oldIndexElement.dataset.pollPopulate;
                var oldValue = null

                if(oldDataPosition == null || oldDataPosition == "" || oldDataPosition == "data"){
                    oldValue = oldIndexElement.dataset.pollData;
                }else if(oldDataPosition == "innerHTML"){
                    oldValue = oldIndexElement.innerHTML;
                }else if(oldDataPosition = "value"){
                    oldValue = oldIndexElement.value;
                }else{
                    console.error("could not find " + oldDataPosition + " of " + oldIndexElement.dataset.poll); 
                }
                if(newData == oldValue){
                    oldRows[x].id = prefix + "_" + x;
                    populateDataRow(oldRows[x], data[y], prefix);
                    index = y;
                    break;
                }

            }
            if (index != -1){
                data.splice(index, 1);
            }
            else{
                //row not in data (outdated)
                oldRows[x].remove();
                x -= 1
            }
        }else{
            //complete update needed
            oldRows[x].remove();
            x -= 1
        }
    }
    //add new and not updatable rows
    for(x = 0; x < data.length; x++){
        var newTableRow = row.cloneNode(true)
        newTableRow.id = prefix + "_" + x
        populateDataRow(newTableRow, data[x], prefix);
        newTableRow.style.display = newDisplay
        body.appendChild(newTableRow)
    }
}
//automatic population of data
//data-poll= prefix_dataDictionaryPath #what data to populate with
//data-poll-populate = data | innerHTML | value //what to populate
//data-poll-data = ... //will be populated with data if data-poll-populate == data | "" | null
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
                    var position = element.dataset.pollPopulate;
                    if(position == null || position == "" || position == "data"){
                        element.dataset.pollData = data;
                    }else if(position == "innerHTML"){
                        element.innerHTML = data;
                    }else if(position = "value"){
                        element.value = data;
                    }else{
                        console.error("could not populate " + position + " of " + element.dataset.poll); 
                    }
                }
            }
        }
    }

    //console.log(tableRow);
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