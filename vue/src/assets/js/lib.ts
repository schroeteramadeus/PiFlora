//data-poll-index = dataKey //unique identifier in order to find updated data
export function populate(body : HTMLTableSectionElement, row : HTMLTableRowElement, data : { [x: string]: any; }, prefix:string, newDisplay:string){
    //delete last rows
    var oldRows:any = body.children;
    for(var x = 0; x < oldRows.length; x++){
        if (oldRows[x].dataset.pollIndex != null){
            var newTableRow : any = row.cloneNode(true)
            var index = -1
            var dictPath = oldRows[x].dataset.pollIndex.split("_").splice(1);

            for(var y = 0; y < data.length; y++){
                var newData = data[y];
                
                while(dictPath.length > 0){
                    newData = newData[dictPath[0]];
                    dictPath = dictPath.splice(1);
                }
                var oldIndexElement:any = oldRows[x].querySelector("[data-poll='" + oldRows[x].dataset.pollIndex + "']");
                if(oldIndexElement != null){
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
        var newTableRow : any = row.cloneNode(true);
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
export function populateDataRow(tableRow : HTMLElement, dataDictionary: { [x: string]: any; }, prefix: string = ""){
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
                var element : any = tableRow.querySelector("*[data-poll=" + prefix + "_" + keys[x] + "]");
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


export function getURIParameters() : URLSearchParams{
    return new URLSearchParams(window.location.search);
}

export function excecuteOnceAfter(func : Function, timer : number){
    var n = setInterval(fadeOut, timer);
    function fadeOut(){
        func();
        clearInterval(n);
    }
}
export function updateSelect(select : HTMLSelectElement, property : string){
    select.style.color = window.getComputedStyle(select.options[select.selectedIndex]).getPropertyValue(property);
}
export function selectValue(select : HTMLSelectElement, value : any) : boolean{
    var success = false;
    for(var x = 0; x < select.options.length; x++){
        if(select.options[x].value == value){
            select.selectedIndex = x;
            success = true;
            break;
        }
    }
    return success;
}
export function switchDisplay(el1 : HTMLElement, el2 : HTMLElement){
    var display = el1.style.display;
    el1.style.display = el2.style.display;
    el2.style.display = display;
}

export function removeOnceFromArray(array:any[], value : any) : any[]{
    var output = []
    var index = array.indexOf(value);
    if (index > -1) {
        output = array.splice(index, 1);
    }
    return output;
}

export function urlToName(url : string): string{
  let name = url
  name = name.replace("https://", "").replace("http://", "").replace("/","_")
  return name  
}
export function eventTargetToElement(eventTarget : EventTarget | null) : HTMLElement | null {
    if(eventTarget != null)
        return eventTarget as HTMLElement;
    else
        return null;
}