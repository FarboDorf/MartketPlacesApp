import datetime
import time

from flask import Flask, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
from markupsafe import escape
import os
# from pprint import pprint
import WB
import Ozon
import folders
import general
import keys

app = Flask(__name__)
sched = BackgroundScheduler(daemon=True)

shops_names = ["Fortuna", "Progress"]
shops_ProgressTest = ["Progress"]
WBAll = {
    "Fortuna": {
        "WBsupplyId": {
            "time": "",
            "supplyId": ""
        },
        "WBsupplyInfo": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "WBorders": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "WBstatus": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "WBstocks": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "WBstickers": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "WBaddToSupply": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "WBsupplyBC": {
            "time": "",
            "code": 0,
            "reason": ""
        }
    },
    "Progress": {
        "WBsupplyId": {
            "time": "",
            "supplyId": ""
        },
        "WBsupplyInfo": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "WBorders": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "WBstatus": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "WBstocks": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "WBstickers": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "WBaddToSupply": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "WBsupplyBC": {
            "time": "",
            "code": 0,
            "reason": ""
        }
    }
}
ozonAll = {
    "Fortuna": {
        "ozonOrders": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "ozonStatus": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "ozonStocks": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "ozonPackageLable": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "ozonActsMainWH": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "ozonActsDistWH": {
            "time": "",
            "code": 0,
            "reason": ""
        }
    },
    "Progress": {
        "ozonOrders": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "ozonStatus": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "ozonStocks": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "ozonPackageLable": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "ozonActsMainWH": {
            "time": "",
            "code": 0,
            "reason": ""
        },
        "ozonActsDistWH": {
            "time": "",
            "code": 0,
            "reason": ""
        }
    }
}


def setExeptionInfo(marketPlace, shop, field, error):
    marketPlace["{}".format(shop)]["{}".format(field)]["time"] = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    marketPlace["{}".format(shop)]["{}".format(field)]["code"] = general.ERROR_CODE
    marketPlace["{}".format(shop)]["{}".format(field)]["reason"] = str(error)


@app.route('/ResponseWBAll')
def ResponseWBAll():
    return WBAll


@app.route('/ResponseAllOzon')
def ResponseAllOzon():
    return ozonAll


@app.route("/")
def index():
    return render_template("index.html")
    # return render_template("index.html", WBAll=WBAll, OzonAll=OzonAll)


# --------------------------------------------------WB------------------------------------------------------------------
@app.route("/<shop>/WBorders")
def WBorders(shop=""):
    if not request:
        for shop in shops_names:
            try:
                WBAll[shop]["WBorders"].update(WB.getOrders(shop))
            except Exception as error:
                setExeptionInfo(WBAll, shop, "WBorders", error)
    else:
        ordersInfo = WB.getOrders(escape(shop))
        WBAll[shop]["WBorders"].update(ordersInfo)
        return ordersInfo


@app.route("/<shop>/WBstatus")
def WBstatus(shop=""):
    if not request:
        for shop in shops_names:
            try:
                WBAll[shop]["WBstatus"].update(WB.sendStatuses(shop))
            except Exception as error:
                setExeptionInfo(WBAll, shop, "WBstatus", error)
    else:
        statusInfo = WB.sendStatuses(shop)
        WBAll[shop]["WBstatus"].update(statusInfo)
        return statusInfo


@app.route("/<shop>/getWBsupplyId")
def WBsupplyId(shop=""):
    if not request:
        for shop in shops_names:
            try:
                WBAll[shop]["WBsupplyId"].update(WB.getSupplyId(shop))
                # for quic update info about supply status
                if("WB" in WBAll[shop]["WBsupplyId"]["supplyId"]):
                    if(WBAll[shop]["WBsupplyInfo"]["reason"] == "Closed"):
                        WBAll[shop]["WBsupplyInfo"]["time"] = WBAll[shop]["WBsupplyId"]["time"]
                        WBAll[shop]["WBsupplyInfo"]["code"] = general.OK_CODE
                        WBAll[shop]["WBsupplyInfo"]["reason"] = "Open"
                else:
                    WBAll[shop]["WBsupplyInfo"]["time"] = WBAll[shop]["WBsupplyId"]["time"]
                    WBAll[shop]["WBsupplyInfo"]["code"] = general.WARNING_CODE
                    WBAll[shop]["WBsupplyInfo"]["reason"] = "Сlosed"
            except Exception as error:
                setExeptionInfo(WBAll, shop, "WBsupplyId", error)
    else:
        supplyIdInfo = WB.getSupplyId(shop)
        WBAll[shop]["WBsupplyId"].update(WB.getSupplyId(shop))
        return supplyIdInfo


@app.route("/<shop>/addToSupply")
def WBaddToSupply(shop=""):
    if not request:
        for shop in shops_ProgressTest:
            try:
                WBAll[shop]["WBaddToSupply"].update(WB.addToSupply(shop, WBAll[shop]["WBsupplyId"]["supplyId"]))
            except Exception as error:
                setExeptionInfo(WBAll, shop, "WBaddToSupply", error)
    else:
        addToSupplyInfo = WB.addToSupply(shop, WBAll[shop]["WBsupplyId"]["supplyId"])
        WBAll[shop]["WBaddToSupply"].update(addToSupplyInfo)
        return addToSupplyInfo


# app.route("/<shop>/WBsupplyBC/", defaults={'supplyId': WBAll[<shop>]["WBsupplyId"]["supplyId"]})
@app.route("/<shop>/WBsupplyBC/")
@app.route("/<shop>/WBsupplyBC/<supplyId>")
def WBsupplyBC(shop="", supplyId=""):
    if not(supplyId):
        supplyId = WBAll[shop]["WBsupplyId"]["supplyId"]
    if not request:
        for shop in shops_names:
            try:
                WBAll[shop]["WBsupplyBC"].update(WB.getSupplyBarcode(shop, supplyId))
            except Exception as error:
                setExeptionInfo(WBAll, shop, "WBsupplyBC", error)
    else:
        supplyBCInfo = WB.getSupplyBarcode(shop, supplyId)
        WBAll[shop]["WBsupplyBC"].update(supplyBCInfo)
        return supplyBCInfo


@app.route("/<shop>/WBshipment")
@app.route("/<shop>/WBshipment/<supplyId>")
def WBshipment(shop="", supplyId=""):
    if(not request):
        # if not command for close supply
        if not(os.listdir(folders.Path().WBCloseSupply("Fortuna"))):
            return
        # delete close command
        os.remove(os.path.join(folders.Path().WBCloseSupply("Fortuna"),
                               os.listdir(folders.Path().WBCloseSupply("Fortuna"))[0]))
        for shop in shops_ProgressTest:
            if not (supplyId):
                supplyId = WBAll[shop]["WBsupplyId"]["supplyId"]
            try:
                # close curent supply
                while(WBAll[shop]["WBsupplyInfo"]["reason"] != "Closed"):
                    WBAll[shop]["WBsupplyInfo"].update(WB.closeSupply(shop, supplyId))
                    time.sleep(10)
                # get order count list in supply
                while(WBAll[shop]["WBsupplyInfo"]["reason"] != "Saved orders count"):
                    WBAll[shop]["WBsupplyInfo"].update(WB.getSupplyOrders(shop, supplyId))
                    time.sleep(10)
                # create new supply
                while(WBAll[shop]["WBsupplyInfo"]["reason"] != "Open"):
                    WBAll[shop]["WBsupplyId"].update(WB.createSupply(shop))
                    time.sleep(10)
                # get supply barcode
                WBAll[shop]["WBsupplyBC"].update(WB.getSupplyBarcode(shop, supplyId))
            except Exception as error:
                print(error)
    else:
        if not(supplyId):
            supplyId = WBAll[shop]["WBsupplyId"]["supplyId"]
        if (os.listdir(folders.Path().WBCloseSupply("Fortuna"))):
            info = {"closeSupply":      WB.closeSupply(shop, supplyId),
                    "getSupplyOrders":  WB.getSupplyOrders(shop, supplyId),
                    "createSupply":     WB.createSupply(shop),
                    "supplyBC":         WB.getSupplyBarcode(shop, supplyId)
                    }
            os.remove(os.listdir(folders.Path().WBCloseSupply("Fortuna"))[0])
        else:
            info = {"getSupplyOrders":  WB.getSupplyOrders(shop, supplyId),
                    "supplyBC":         WB.getSupplyBarcode(shop, supplyId)
                    }
        WBAll[shop]["WBsupplyInfo"].update(info["getSupplyOrders"])
        WBAll[shop]["WBsupplyBC"].update(info["supplyBC"])

        return info


@app.route("/<shop>/WBstocks")
def WBstocks(shop=""):
    if not request:
        for shop in shops_names:
            try:
                # WBAll.update({"{}".format(shop): {"WBstatus": WB.sendStatuses(shop)}})
                WBAll[shop]["WBstocks"].update(WB.sendStocks(shop))
            except Exception as error:
                setExeptionInfo(WBAll, shop, "WBstocks", error)
    else:
        stockInfo = WB.sendStocks(shop)
        WBAll[shop]["WBstocks"].update(stockInfo)
        return stockInfo


@app.route("/<shop>/WBstickers")
def WBstickers(shop=""):
    if not request:
        for shop in shops_names:
            try:
                WBAll[shop]["WBstickers"].update(WB.getStickers(shop))
            except Exception as error:
                setExeptionInfo(WBAll, shop, "WBstickers", error)
    else:
        stickerInfo = WB.getStickers(shop)
        WBAll[shop]["WBstickers"].update(stickerInfo)
        return stickerInfo


# ------------------------------------------------OZON------------------------------------------------------------------
@app.route("/<shop>/OzonOrders")
def OzonOrders(shop=""):
    if not request:
        for shop in shops_names:
            try:
                ozonAll[shop]["ozonOrders"].update(Ozon.getOrders(shop))
            except Exception as error:
                setExeptionInfo(ozonAll, shop, "ozonOrders", error)
    else:
        orderInfo = Ozon.getOrders(shop)
        ozonAll[shop]["ozonOrders"].update(orderInfo)
        return orderInfo


@app.route("/<shop>/OzonStatus")
def OzonStatus(shop=""):
    if not request:
        for shop in shops_names:
            try:
                ozonAll[shop]["ozonStatus"].update(Ozon.sendStatuses(shop))
            except Exception as error:
                setExeptionInfo(ozonAll, shop, "ozonStatus", error)
    else:
        statusInfo = Ozon.sendStatuses(shop)
        ozonAll[shop]["ozonStatus"].update(statusInfo)
        return statusInfo


@app.route("/<shop>/OzonStocks")
def OzonStocks(shop=""):
    if not request:
        for shop in shops_names:
            try:
                ozonAll[shop]["ozonStocks"].update(Ozon.sendStocks(shop))
            except Exception as error:
                setExeptionInfo(ozonAll, shop, "ozonStocks", error)
    else:
        stocksInfo = Ozon.sendStocks(shop)
        ozonAll[shop]["ozonStocks"].update(stocksInfo)
        return stocksInfo


@app.route("/<shop>/OzonPL")
def OzonPL(shop=""):
    if not request:
        for shop in shops_names:
            try:
                ozonAll[shop]["ozonPackageLable"].update(Ozon.getPackageLabel(shop))
            except Exception as error:
                setExeptionInfo(ozonAll, shop, "ozonPackageLable", error)
    else:
        packageLabelInfo = Ozon.getPackageLabel(shop)
        ozonAll[shop]["ozonPackageLable"].update(packageLabelInfo)
        return packageLabelInfo


@app.route("/<shop>/OzonActs/<int:warehouseID>")
def OzonAct(shop, warehouseID):
    WHType = "ozonActs"
    if(warehouseID == 20576832430000 or warehouseID == 22265706608000):
        WHType += "MainWH"
    elif(warehouseID == 22193730429000 or warehouseID == 22267367864000):
        WHType += "DistWH"

    # getting act id
    reqCnt = 0
    # for faster stop
    if(request):
        reqCnt += 110

    while(True):
        actID, actInfo = Ozon.getActID(shop, warehouseID)
        ozonAll[shop][WHType].update(actInfo)
        reqCnt += 1
        if(actID != 0):
            break
        if(reqCnt >= 150):
            return ozonAll[shop][WHType]
        time.sleep(60)

    # check act readiness
    while(True):
        if("Main" in WHType):
            wh = "Main"
        if("Dist" in WHType):
            wh = "Dist"
        readiness, actInfo = Ozon.readinessAct(shop, wh, actID)
        ozonAll[shop][WHType].update(actInfo)
        if(readiness):
            break
        time.sleep(60)

    # get and save act
    ozonAll[shop][WHType].update(Ozon.getAct(shop, wh, actID))

    if(request):
        return ozonAll[shop][WHType]


if __name__ == '__main__':
    from waitress import serve

    sched.add_job(WBorders,      trigger="interval", minutes=15)
    sched.add_job(WBstatus,      trigger="interval", minutes=1, seconds=30)

    sched.add_job(WBsupplyId,    trigger="interval", minutes=1)
    # sched.add_job(WBaddToSupply, trigger="interval", minutes=1, seconds=30)
    # sched.add_job(WBshipment, trigger="interval", minutes=1)

    sched.add_job(WBstocks,      trigger="interval", minutes=3)
    sched.add_job(WBstickers,    trigger="interval", minutes=2)

    sched.add_job(OzonOrders,    trigger="interval", minutes=15)
    sched.add_job(OzonStatus,    trigger="interval", minutes=1)
    sched.add_job(OzonStocks,    trigger="interval", minutes=15)
    sched.add_job(OzonPL,        trigger="interval", minutes=1)

    sched.add_job(OzonAct, trigger="cron",
                  args=["Fortuna", keys.shops["Fortuna"]["mainWHID"]],   day_of_week='mon-fri', hour=11, minute=15)
    sched.add_job(OzonAct, trigger="cron",
                  args=["Fortuna", keys.shops["Fortuna"]["distWHID"]],   day_of_week='mon-fri', hour=11, minute=20)

    sched.add_job(OzonAct, trigger="cron",
                  args=["Progress", keys.shops["Progress"]["mainWHID"]], day_of_week='mon-fri', hour=11, minute=16)
    sched.add_job(OzonAct, trigger="cron",
                  args=["Progress", keys.shops["Progress"]["distWHID"]], day_of_week='mon-fri', hour=11, minute=17)

    sched.start()

    serve(app, host="0.0.0.0", port=7000)

