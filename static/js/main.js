"use strict";
const URL = "http://192.168.0.55:8080/";

let checkBoxes = document.getElementsByClassName("form-check-input");
[].forEach.call(checkBoxes, function (el) {
    el.addEventListener('click', function (e) {
        el.checked = !el.checked;
    })
});


function fillInfo(info, checkBox, dateAndTime, status, feedBack){
    if(info.code == 0){
        return;
    }
    if(info.code == 999){
        checkBox.checked = false;
        if (!status.classList.contains("is-invalid")) {
            status.classList.toggle("is-invalid");
            feedBack.classList.toggle("invalid-feedback");
        }
    }
    else{
        checkBox.checked = true;
        if(info.code == 200) {
            status.classList.remove("border-warning")
            status.classList.remove("is-invalid")
            if (!status.classList.contains("is-valid")) {
                status.classList.toggle("is-valid");
            }
        }
        else{
            status.classList.remove("is-invalid")
            if (!status.classList.contains("border-warning")) {
                status.classList.toggle("border-warning");
            }
        }
    }
    dateAndTime.innerHTML = info.time;
    status.value = info.reason;
    if(info.reason.includes("Errno 11001")){
        feedBack.innerHTML = "Ошибка сети";
    }
}


function makeRequest(e){
    let shop = "";
    let whID = "";
    let id = String(e.target.id);

    if(id.includes("Fortuna")){
            shop = "Fortuna";
            if(id.includes("Main")){
            whID = "20576832430000"
            }
            if(id.includes("Dist")){
                whID = "22193730429000"
            }
        }
    if(id.includes("Progress")){
        shop = "Progress";
        if(id.includes("Main")){
        whID = "22265706608000"
        }
        if(id.includes("Dist")){
            whID = "22267367864000"
        }
    }
    let settings = {
        "url": URL + shop + "/OzonActs/" + whID,
        "method": "GET",
        "timeout": 0,
    };
    $.ajax(settings).done(function(response){
        console.log(response)
    })
}


downloadActFortunaMainWH.onclick = makeRequest;
downloadActFortunaDistWH.onclick = makeRequest;

downloadActProgressMainWH.onclick = makeRequest;
downloadActProgressDistWH.onclick = makeRequest;



setInterval(function get_values() {
    let settingsWB = {
        "url": URL + "ResponseWBAll",
        "method": "GET",
        "timeout": 0,
    };
    let settingsOzon = {
        "url": URL + "ResponseAllOzon",
        "method": "GET",
        "timeout": 0,
    };


    //WB
    $.ajax(settingsWB).done(function (response) {
        console.log("WB  ", response);

        supplyIdFortuna.value = response.Fortuna.WBsupplyId.supplyId;
        supplyIdProgress.value = response.Progress.WBsupplyId.supplyId;

        fillInfo(response.Fortuna.WBorders, checkOrdersWBFortuna, ordersDateTimeWBFortuna, ordersStatusWBFortuna, ordersFeedBackWBFortuna);
        fillInfo(response.Progress.WBorders, checkOrdersWBProgress, ordersDateTimeWBProgress, ordersStatusWBProgress, ordersFeedBackWBProgress);

        fillInfo(response.Fortuna.WBstatus, checkOrdStatusWBFortuna, ordStatusDateTimeWBFortuna, ordStatusStatusWBFortuna, ordStatusFeedBackWBFortuna)
        fillInfo(response.Progress.WBstatus, checkOrdStatusWBProgress, ordStatusDateTimeWBProgress, ordStatusStatusWBProgress, ordStatusFeedBackWBProgress)

        fillInfo(response.Fortuna.WBstocks, checkStocksWBFortuna, stocksDateTimeWBFortuna, stocksStatusWBFortuna, stocksFeedBackWBFortuna)
        fillInfo(response.Progress.WBstocks, checkStocksWBProgress, stocksDateTimeWBProgress, stocksStatusWBProgress, stocksFeedBackWBProgress)

        fillInfo(response.Fortuna.WBstickers, checkStickersWBFortuna, stickersDateTimeWBFortuna, stickersStatusWBFortuna, stickersFeedBackWBFortuna)
        fillInfo(response.Progress.WBstickers, checkStickersWBProgress, stickersDateTimeWBProgress, stickersStatusWBProgress, stickersFeedBackWBProgress)

        fillInfo(response.Fortuna.WBsupplyInfo, checkSupplyInfoWBFortuna, supplyInfoDateTimeWBFortuna, supplyInfoStatusWBFortuna, supplyInfoFeedBackWBFortuna)
        fillInfo(response.Progress.WBsupplyInfo, checkSupplyInfoWBProgress, supplyInfoDateTimeWBProgress, supplyInfoStatusWBProgress, supplyInfoFeedBackWBProgress)

        fillInfo(response.Fortuna.WBsupplyBC, checkSupplyBCWBFortuna, supplyBCDateTimeWBFortuna, supplyBCStatusWBFortuna, supplyBCFeedBackWBFortuna)
        fillInfo(response.Progress.WBsupplyBC, checkSupplyBCWBProgress, supplyBCDateTimeWBProgress, supplyBCStatusWBProgress, supplyBCFeedBackWBProgress)

        fillInfo(response.Fortuna.WBaddToSupply, checkSuppliesWBFortuna, suppliesDateTimeWBFortuna, suppliesStatusWBFortuna, suppliesFeedBackWBFortuna)
        fillInfo(response.Progress.WBaddToSupply, checkSuppliesWBProgress, suppliesDateTimeWBProgress, suppliesStatusWBProgress, suppliesFeedBackWBProgress)
    });


    //Ozon
    $.ajax(settingsOzon).done(function (response) {
        console.log("Ozon", response);
        fillInfo(response.Fortuna.ozonOrders, checkOrdersOzonFortuna, ordersDateTimeOzonFortuna, ordersStatusOzonFortuna, ordersFeedBackOzonFortuna);
        fillInfo(response.Progress.ozonOrders, checkOrdersOzonProgress, ordersDateTimeOzonProgress, ordersStatusOzonProgress, ordersFeedBackOzonProgress);

        fillInfo(response.Fortuna.ozonStatus, checkOrdStatusOzonFortuna, ordStatusDateTimeOzonFortuna, ordStatusStatusOzonFortuna, ordStatusFeedBackOzonFortuna)
        fillInfo(response.Progress.ozonStatus, checkOrdStatusOzonProgress, ordStatusDateTimeOzonProgress, ordStatusStatusOzonProgress, ordStatusFeedBackOzonProgress)

        fillInfo(response.Fortuna.ozonStocks, checkStocksOzonFortuna, stocksDateTimeOzonFortuna, stocksStatusOzonFortuna, stocksFeedBackOzonFortuna)
        fillInfo(response.Progress.ozonStocks, checkStocksOzonProgress, stocksDateTimeOzonProgress, stocksStatusOzonProgress, stocksFeedBackOzonProgress)

        fillInfo(response.Fortuna.ozonPackageLable, checkPLOzonFortuna, PLDateTimeOzonFortuna, PLStatusOzonFortuna, PLFeedBackOzonFortuna)
        fillInfo(response.Progress.ozonPackageLable, checkPLOzonProgress, PLDateTimeOzonProgress, PLStatusOzonProgress, PLFeedBackOzonProgress)

        fillInfo(response.Fortuna.ozonActsMainWH, checkActOzonFortuna, ActDateTimeOzonMainWHFortuna, ActStatusOzonMainWHFortuna, ActFeedBackOzonMainWHFortuna)
        fillInfo(response.Fortuna.ozonActsDistWH, checkActOzonFortuna, ActDateTimeOzonDistWHFortuna, ActStatusOzonDistWHFortuna, ActFeedBackOzonDistWHFortuna)
        fillInfo(response.Progress.ozonActsMainWH, checkActOzonProgress, ActDateTimeOzonMainWHProgress, ActStatusOzonMainWHProgress, ActFeedBackOzonMainWHProgress)
        fillInfo(response.Progress.ozonActsDistWH, checkActOzonProgress, ActDateTimeOzonDistWHProgress, ActStatusOzonDistWHProgress, ActFeedBackOzonDistWHProgress)
    });
}, 5000)
