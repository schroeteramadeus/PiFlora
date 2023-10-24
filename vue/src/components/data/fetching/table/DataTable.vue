<script setup lang="ts">
import { ref, onUnmounted, onMounted, defineComponent, useSlots, type Slot, type RendererElement, type RendererNode, type VNode} from 'vue';
import { computed } from '@vue/reactivity';
import {populate} from "@/assets/js/lib"
import {defineTableDataStore} from "@/stores/TableDataStore"
import DataTableColumnGroup from './DataTableColumnGroup.vue';
import DataTableColumn from './DataTableColumn.vue';
import { StatusVars } from '@/data/StatusVars';

let props = defineProps({
  url: {
    type: String, 
    required: true,
  },
  updateTime: {
    type: Number, 
    required: false,
    default: 5000,
  },
});

let dataTableStore = defineTableDataStore(props.url).get();

let name = dataTableStore.$id;

let defaultRow:HTMLTableRowElement|null = null;

const slots = useSlots();
const columns = slots.default ? slots.default() : null;

function createDefaultRow() : HTMLTableRowElement{
    defaultRow = document.createElement("tr");
    if(columns != null){
        for(var x = 0; x < columns.length; x++){
            var p = columns[x].props;
            
            if(p != null){
                if(columns[x].type == DataTableColumnGroup){

                }else if(columns[x].type == DataTableColumn){
                    var cell = document.createElement("td");
                    cell.dataset.poll = p["poll-path"] as string;
                    //cell.dataset.pollStatus = StatusVars.POLLSTATUSPOLLING;
                    cell.dataset.pollPopulate = "innerHTML";
                    cell.innerHTML = "ERROR";

                    defaultRow.appendChild(cell)
                }
            }
        }
    }
    return defaultRow;
}
function populateTableRow(tableRow : HTMLTableRowElement, dataDictionary: { [x: string]: any; }, prefix:string = ""){
    var keys = Object.keys(dataDictionary)
    //console.log(keys);
    for(var x = 0; x < keys.length; x++){
        var data = dataDictionary[keys[x]];    
        //console.log(keys[x] + " | " + data);
        //data == dictionary
        if (data.constructor == Object) {
            populateTableRow(tableRow, data, prefix == "" ? keys[x] : prefix + "_" + keys[x]);
        }else{
            //console.log("try populate: " + prefix + keys[x] + " with " + data);
            if (tableRow.getAttribute("data-poll") == prefix + keys[x]){
                tableRow.innerHTML = data
            }else{
                var elements : any = tableRow.querySelectorAll("*[data-poll=" + prefix + keys[x] + "]");
                
                for(var y = 0; y < elements.length; y++){
                    var element = elements[y]; 
                    //console.log("populate: " + prefix + keys[x] + " with " + data);
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
}
function populateTable(){
    if(!dataTableStore.data.errorSet && dataTableStore.initialized){
        let data = dataTableStore.data.data

        let tablesToUpdate = document.querySelectorAll("[name='" + name + "']");
        
        for(var tableIndex = 0; tableIndex < tablesToUpdate.length; tableIndex++){
            let table = tablesToUpdate[tableIndex] as HTMLTableElement;
    
            var dataLabel = Object.keys(data)[0];

            if(data[dataLabel].length > 0){
                data = data[dataLabel];
                //console.log(data);
                if(defaultRow == null){
                    defaultRow = createDefaultRow();
                }
                var tableBody = table.children[1];
                var oldRows:any = tableBody.children;
                for(var x = 0; x < oldRows.length; x++){
                    if (oldRows[x].dataset.pollIndex != null){
                        var newTableRow : any = defaultRow.cloneNode(true)
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
                                    //oldRows[x].id = prefix + "_" + x;
                                    populateTableRow(oldRows[x], data[y]);
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
                    var newTableRow : any = defaultRow.cloneNode(true);
                    //newTableRow.id = prefix + "_" + x
                    populateTableRow(newTableRow, data[x]);
                    //newTableRow.style.display = newDisplay
                    tableBody.appendChild(newTableRow)
                }
            }
        }
    }else{
        //TODO log?
    }
}

/*
for(var dataIndex = 0; dataIndex < data[dataLabel].length; dataIndex++){
    var dataSet: { [x: string]: any; } = data[dataLabel][dataIndex];
    //TODO check key (for smart update)
    var newRow = defaultRow.cloneNode(true) as HTMLTableRowElement;
    populateTableRow(newRow, dataSet);
    table.children[1].appendChild(newRow);
}
*/

function onUpdate(){
    dataTableStore.update();
    populateTable()
}

onMounted(()=>{
    populateTable();
    onUpdate();
    dataTableStore.setUpdateInterval(onUpdate, props.updateTime);
})
onUnmounted(()=>{
    dataTableStore.clearUpdateInterval();
})

</script>

<template>
    <table :name=name>
        <thead>
            <slot name="default"></slot>
        </thead>
        <tbody>
            
        </tbody>
    </table>
</template>

<style scoped>

</style>