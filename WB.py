import requests
import pandas as pd
import datetime
import pytz
import base64
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import os

import general
from ApiClient import WBApi
import folders
from general import organizeData


directories = folders.Path()
WBApi = WBApi()


def fail():
    print("fail_function")
    ordersInfo = {
                "time": "12.15",
                "code": 1/0,
                "reason": "!"
            }
    return ordersInfo


# ________________________________________________ORDERS________________________________________________________________
def getOrders(shop):
    print(shop)
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    dateStart = ((datetimeMSK - datetime.timedelta(days=3))
                 .replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None).isoformat())
    ordersDirectory = directories.WBOrders(shop) + "WBOrders" + str(datetimeMSK.date()) + ".xls"

    skip = 0
    allOrders = pd.DataFrame()
    # request
    while(True):
        ordersURL = WBApi.baseOrdersURL + dateStart + "Z&status=0&take=1000&skip=" + str(skip)
        try:
            res = requests.get(ordersURL, headers=WBApi.headers(shop))
            print(datetimeMSK.replace(microsecond=0, tzinfo=None))
            print("Orders:", res.status_code, res.reason)
            ordersInfo = {
                "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
                "code": res.status_code,
                "reason": res.reason
            }
            allOrders = pd.concat([allOrders, pd.json_normalize(res.json(), "orders")], ignore_index=True)
            # print(res.text)
            print()
        except Exception as error:
            print(error)
            return str(error)
            # continue
        skip += 1000
        if(res.json()["total"] < skip):
            if(res.json()["total"] == 0):
                ordersInfo["code"] = general.OK_CODE
                ordersInfo["reason"] = "There are no new orders"
                with open(directories.WBLogs(shop) + "WBLogOrders.txt", "w") as log:
                    log.write(str(datetimeMSK) + "\n" + str(ordersInfo["reason"]))
                return ordersInfo
            break
    # save response
    try:
        # II slow method (~15 minutes between get order and sticker)
        getStickersFromOrderList(shop)

        newCols = ["orderId", "chrtId", "status", "rid", "totalPrice",
                   "sticker.wbStickerId", "dateCreated", "userStatus"]
        allOrders = (allOrders.reindex(columns=newCols).
                     rename(columns={'status': 'order_status',
                                     'sticker.wbStickerIdParts.A': 'Barcode_A',
                                     'sticker.wbStickerIdParts.B': 'Barcode_B'}))

        allOrders = allOrders.drop_duplicates(subset=allOrders.columns.values[:-1])
        allOrders["dateCreated"] = pd.to_datetime(allOrders["dateCreated"]).dt.tz_localize(None)
        pd.DataFrame(allOrders.to_excel(ordersDirectory, index=False))

        with open(directories.WBLogs(shop) + "WBLogOrders.txt", "w") as log:
            log.write(str(datetimeMSK) + "\nOK")

        return ordersInfo

    except Exception as error:
        print(error)
        ordersInfo["code"] = general.WARNING_CODE
        ordersInfo["reason"] = str(error)
        return ordersInfo


# ________________________________________________STATUS________________________________________________________________
def sendStatuses(shop):
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    statusInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": [],
        "reason": []
    }
    # dateStart = UTCDateMSK.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    try:
        files = os.listdir(directories.WBStatus(shop))
        files = [os.path.join(directories.WBStatus(shop), file) for file in files]
    except Exception as error:
        print(error)
        statusInfo["code"] = general.WARNING_CODE
        statusInfo["reason"] = str(error)
        return str(error)

    for file in sorted(files, key=os.path.getmtime):
        if (not os.path.isfile(file)):
            continue
        print(shop)
        print(datetimeMSK.replace(microsecond=0, tzinfo=None))
        print(os.path.basename(file))

        try:
            df = pd.read_excel(file)
            df = df.drop(columns="rid")
            df["Order_id"] = df["Order_id"].astype(str)
            df = df.rename(columns={"Order_id": "orderId", "Status": "status"})
            payload = df.to_dict("records")
        except Exception as error:
            print(error)
            statusInfo["code"].append(general.WARNING_CODE)
            statusInfo["reason"].append(str(error))
            # return str(error)
            continue

        # print(payload)

        try:
            res = requests.put(WBApi.statusURL, headers=WBApi.headers(shop), json=payload)
            print("status:", res.status_code, res.reason)
            statusInfo["code"].append(res.status_code)
            statusInfo["reason"].append(res.reason)
            if (res.status_code == 200):
                os.remove(file)
            else:
                print(res.text)
            print()

        except Exception as error:
            print(error)
            statusInfo["code"].append(general.WARNING_CODE)
            statusInfo["reason"].append(str(error))
            return statusInfo

    return organizeData(statusInfo, general.OK_CODE, "There are no new status")


# _______________________________________________SUPPLIES_______________________________________________________________
def getSupplyId(shop):
    param = "?status=ACTIVE"
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    supplyIdInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "supplyId": ""
    }
    try:
        res = requests.get(WBApi.supplyIdURL + param, headers=WBApi.headers(shop))
        print("get supply id", res.status_code, res.reason)
        if(res.status_code == 200 and res.json()["supplies"]):
            supplyIdInfo["supplyId"] = res.json()["supplies"][0]["supplyId"]
            return supplyIdInfo
    except Exception as error:
        print(error)
        return str(error)
    else:
        supplyIdInfo["supplyId"] = "There are no supply"
        return supplyIdInfo


def createSupply(shop):
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    createSupplyInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": 0,
        "reason": ""
    }
    try:
        res = requests.post(WBApi.supplyIdURL, headers=WBApi.headers(shop))
        print("get supply id", res.status_code, res.reason)
        createSupplyInfo["code"] = res.status_code
        createSupplyInfo["reason"] = "Open"
    except Exception as error:
        createSupplyInfo["code"] = general.WARNING_CODE
        createSupplyInfo["reason"] = str(error)
        print(error)
    finally:
        return createSupplyInfo


def addToSupply(shop, supplyId):
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    supplyInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": [],
        "reason": []
    }

    if ("WB" not in supplyId):
        supplyInfo["code"] = general.OK_CODE
        supplyInfo["reason"] = supplyId + " for add orders"
        return supplyInfo

    try:
        files = os.listdir(directories.WBSupplyList(shop))
        files = [os.path.join(directories.WBSupplyList(shop), file) for file in files]
    except Exception as error:
        print(error)
        supplyInfo["code"] = general.WARNING_CODE
        supplyInfo["reason"] = str(error)
        return str(error)

    for file in sorted(files, key=os.path.getmtime):
        if (not os.path.isfile(file)):
            continue
        print(shop)
        print(datetimeMSK.replace(microsecond=0, tzinfo=None))
        print(os.path.basename(file))

        try:
            df = pd.read_excel(file)
            df["OrderId"] = df["OrderId"].astype(str)
            df = df.rename(columns={"OrderId": "orders"})
            payload = df.to_dict("list")
        except Exception as error:
            print(error)
            supplyInfo["code"].append(general.WARNING_CODE)
            supplyInfo["reason"].append(str(error))
            continue

        try:
            res = requests.put(WBApi.addSupplyURL(supplyId), headers=WBApi.headers(shop), json=payload)
            print("addToSupply:", res.status_code, res.reason)
            supplyInfo["code"].append(res.status_code)
            supplyInfo["reason"].append(res.reason)
            if (res.status_code == 204):  # specific code
                os.remove(file)
            else:
                print(res.text)
            print()

        except Exception as error:
            print(error)
            supplyInfo["code"].append(general.WARNING_CODE)
            supplyInfo["reason"].append(str(error))
            return supplyInfo

    return organizeData(supplyInfo, general.OK_CODE, "There are no new orders for add to supply")


def closeSupply(shop, supplyId):
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    closeSupplyInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": 0,
        "reason": ""
    }

    if ("WB" not in supplyId):
        closeSupplyInfo["code"] = general.WARNING_CODE
        closeSupplyInfo["reason"] = supplyId + " for close"
        return closeSupplyInfo

    try:
        res = requests.post(WBApi.closeSupplyURL(supplyId), headers=WBApi.headers(shop))
        print("close supply", res.status_code, res.reason)
        closeSupplyInfo["code"] = res.status_code
        closeSupplyInfo["reason"] = "Closed"
    except Exception as error:
        closeSupplyInfo["code"] = general.WARNING_CODE
        closeSupplyInfo["reason"] = str(error)
        print(error)
    finally:
        return closeSupplyInfo


def getSupplyOrders(shop, supplyId):
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    supplyOrdersInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": 0,
        "reason": ""
    }
    if ("WB" not in supplyId):
        supplyOrdersInfo["code"] = general.WARNING_CODE
        supplyOrdersInfo["reason"] = supplyId + " for count orders"
        return supplyOrdersInfo

    try:
        res = requests.get(WBApi.supplyOrdersURL(supplyId), headers=WBApi.headers(shop))
        print("get supply order list", res.status_code, res.reason)
    except Exception as error:
        print(error)
        supplyOrdersInfo["code"] = general.WARNING_CODE
        supplyOrdersInfo["reason"] = str(error)
        return supplyOrdersInfo

    fileName = shop + str(datetime.datetime.today().strftime("%d")) + ".txt"
    try:
        with open(os.path.join(directories.WBSupplyOrdersCnt(), fileName), "w") as f:
            f.write(str(len(res.json()["orders"])))
        if(os.path.exists(os.path.join(directories.WBSupplyOrdersCnt(), fileName))):
            supplyOrdersInfo["code"] = general.OK_CODE
            supplyOrdersInfo["reason"] = "Saved orders count"
    except Exception as error:
        print(error)
        supplyOrdersInfo["code"] = general.WARNING_CODE
        supplyOrdersInfo["reason"] = str(error)
    finally:
        return supplyOrdersInfo


def getSupplyBarcode(shop, supplyId):
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    supplyBarcodeInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": 0,
        "reason": ""
    }
    if ("WB" not in supplyId):
        supplyBarcodeInfo["code"] = general.WARNING_CODE
        supplyBarcodeInfo["reason"] = supplyId
        return supplyBarcodeInfo

    param = "?type=svg"
    try:
        res = requests.get(WBApi.supplyBarcodeURL(supplyId) + param, headers=WBApi.headers(shop))
        print("supply barcode", res.status_code, res.reason)
        supplyBarcodeInfo["code"] = res.status_code
        supplyBarcodeInfo["reason"] = res.reason
    except Exception as error:
        print(error)
        supplyBarcodeInfo["code"] = general.WARNING_CODE
        supplyBarcodeInfo["reason"] = str(error)
        return supplyBarcodeInfo

    try:
        barcode = base64.b64decode(res.json()["file"].encode('ascii'))
        fileName = shop + str(datetime.datetime.today().strftime("%d"))
        saveBarcode(directories.WBSupplyBarcode(shop), fileName + ".svg", barcode)
        supplyBarcodeInfo["code"] = general.OK_CODE
        supplyBarcodeInfo["reason"] = "Saved"
    except Exception as error:
        print(error)
        supplyBarcodeInfo["code"] = general.WARNING_CODE
        supplyBarcodeInfo["reason"] = str(error)
    finally:
        supplyBarcodeInfo["time"] = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
        return supplyBarcodeInfo


# ________________________________________________STOCKS________________________________________________________________
def getStocks(shop):
    skip = 0
    allStocks = pd.DataFrame()
    while(True):
        params = "?skip=" + str(skip) + "&take=1000&sort=barcode"
        try:
            res = requests.get(WBApi.stocksURL + params, headers=WBApi.headers(shop))
            # print(res.text)
        except Exception as error:
            print(error)
            continue

        try:
            stocks = pd.json_normalize(res.json(), "stocks").reindex(columns=["barcode", "stock"])
            allStocks = pd.concat([allStocks, stocks], ignore_index=True)
        except Exception as error:
            print(error)

        skip += 1000
        if(res.json()["total"] < skip):
            return allStocks


def sendStocks(shop):
    print(shop)
    if(shop == "Fortuna"):
        warehouseID = 6339
    elif(shop == "Progress"):
        warehouseID = 40354
    else:
        return
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    stocksInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": 0,
        "reason": ""
    }

    # get list of current stocs for adding to request
    curStocks = getStocks(shop)
    curStocks["stock"] = 0

    try:
        newStocks = pd.read_excel(directories.WBStocks(shop) + "Остатки.xls")
    except Exception as error:
        print(error)
        stocksInfo["code"] = general.WARNING_CODE
        stocksInfo["reason"] = str(error)
        return stocksInfo

    newStocks["barcode"] = newStocks["barcode"].astype(str)
    df = pd.concat([newStocks, curStocks], ignore_index=True).drop_duplicates("barcode", ignore_index=False)
    df["warehouseId"] = warehouseID
    df["barcode"] = df["barcode"].astype(str)
    df["stock"] = df["stock"].astype(int)
    payload = df.to_dict("records")

    try:
        res = requests.post(WBApi.stocksURL, headers=WBApi.headers(shop), json=payload)
        print(res.text)
        stocksInfo["code"] = res.status_code
        stocksInfo["reason"] = res.reason
        print(datetimeMSK.replace(microsecond=0, tzinfo=None))
        print("Stocks:", res.status_code, res.reason)
        if (res.status_code != 200):
            print(res.text)
    except Exception as error:
        print(error)
        stocksInfo["code"] = general.WARNING_CODE
        stocksInfo["reason"] = str(error)
    finally:
        return stocksInfo


# ________________________________________________STICKERS______________________________________________________________
def saveBarcode(folder, fileName, barcodeASCII):
    with open(folder + fileName, "wb") as file:
        file.write(barcodeASCII)
    barcocdePic = svg2rlg(folder + fileName)
    renderPM.drawToFile(barcocdePic, folder + fileName.replace("svg", "jpg"), fmt="JPG")

    for file in os.listdir(folder):
        if file.endswith(".svg"):
            os.remove(os.path.join(folder, file))


def getStickers(shop):
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    stickersInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": [],
        "reason": []
    }

    try:
        files = os.listdir(directories.WBOrderList(shop))
        files = [os.path.join(directories.WBOrderList(shop), file) for file in files]
    except Exception as error:
        print(error)
        return str(error)

    for file in sorted(files, key=os.path.getmtime):
        if (not os.path.isfile(file)):
            continue
        print(shop)
        print(datetimeMSK.replace(microsecond=0, tzinfo=None))
        print(os.path.basename(file))

        try:
            df = pd.read_excel(file, header=None)
        except Exception as error:
            print(error)
            continue
            # return str(error)
        payload = {"orderIds": list(df[0])}

        try:
            res = requests.post(WBApi.stickersURL, headers=WBApi.headers(shop), json=payload)
            print("stickers:", res.status_code, res.reason)
            stickersInfo["code"].append(res.status_code)
            stickersInfo["reason"].append(res.reason)
            if (res.status_code == 200 and res.json()["data"]):
                os.remove(file)
            else:
                print(res.text)

            for order in res.json()["data"]:
                sticker = order["sticker"]["wbStickerSvgBase64"]
                barcodeASCII = base64.b64decode(sticker.encode('ascii'))
                fileName = str(order["orderId"])
                if not (os.path.exists(directories.WBBarcodes(shop) + fileName + ".jpg")):
                    saveBarcode(directories.WBBarcodes(shop), fileName + ".svg", barcodeASCII)

        except Exception as error:
            print(error)
            stickersInfo["code"].append(general.WARNING_CODE)
            stickersInfo["reason"].append(str(error))
            return stickersInfo

    return organizeData(stickersInfo, general.OK_CODE, "There are no new stickers")


def getStickersFromOrderList(shop):
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    dateStart = ((datetimeMSK - datetime.timedelta(days=3))
                 .replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None).isoformat())
    allOrders = pd.DataFrame()
    skip = 0
    # request
    while (True):
        ordersURL = WBApi.baseOrdersURL + dateStart + "Z&take=1000&skip=" + str(skip)
        # ordersURL = WBApi.baseOrdersURL + dateStart + "Z&status=1&take=1000&skip=" + str(skip)
        try:
            res = requests.get(ordersURL, headers=WBApi.headers(shop))
            print(datetimeMSK.replace(microsecond=0, tzinfo=None))
            print("Orders list for stickers", res.status_code, res.reason)
            allOrders = pd.concat([allOrders, pd.json_normalize(res.json(), "orders")], ignore_index=True)
            # print(res.text)
            # break
            print()
        except Exception as error:
            print(error)
            return str(error)
            # continue
        skip += 1000
        if (res.json()["total"] < skip):
            break
    if (allOrders.empty):
        return
    newOrderId = {"orderIds": list(allOrders["orderId"].astype(int))}

    try:
        res = requests.post(WBApi.stickersURL, headers=WBApi.headers(shop), json=newOrderId)
        print("stickers:", res.status_code, res.reason)
        if(res.status_code != 200):
            print(res.text)

        for order in res.json()["data"]:
            sticker = order["sticker"]["wbStickerSvgBase64"]
            barcodeASCII = base64.b64decode(sticker.encode('ascii'))
            fileName = str(order["orderId"])
            if not (os.path.exists(directories.WBBarcodes(shop) + fileName + ".jpg")):
                print(fileName)
                saveBarcode(directories.WBBarcodes(shop), fileName + ".svg", barcodeASCII)

    except Exception as error:
        print(error)
