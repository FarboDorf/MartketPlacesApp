import requests
import pandas as pd
import numpy as np
import datetime
import pytz
import os
import tempfile
import math
from pdf2image import convert_from_bytes
import folders
import general
import keys
from ApiClient import OzonApi
from general import organizeData

directories = folders.Path()
ozonApi = OzonApi()


# ________________________________________________ORDERS________________________________________________________________
def getOrderInfo(shop, orderNum):
    payloadInfo = {
        "posting_number": orderNum,
        "with": {
            "analytics_data": False,
            "barcodes": False,
            "financial_data": False
        }
    }
    try:
        res = requests.post(ozonApi.ordersInfoURL, headers=ozonApi.headers(shop), json=payloadInfo)
        print(orderNum, res.status_code, res.reason)
        df = pd.json_normalize(res.json())
        return pd.DataFrame({
            "posting_number": df["result.posting_number"].values,
            "buyer": df["result.addressee.name"].values})
    except Exception as error:
        print(error)
        return pd.DataFrame()


def getOrders(shop):
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    dateStart = (datetimeMSK - datetime.timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)

    ordersInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": [],
        "reason": []
    }
    print(shop)
    while(dateStart < datetimeMSK):
        dateEnd = (dateStart + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        ordersDirectory = (directories.ozonOrders(shop)
                           + "OzonOrders" + str(dateStart.date()) + "T" + str(dateStart.time().hour) + ".xls")

        payloadOrders = {
            "dir": "asc",
            "filter": {
                "since": dateStart.isoformat(),
                "status": "awaiting_packaging",
                "to": dateEnd.isoformat(),
            },
            "limit": 50,
            "with": {
                "barcodes": False
            }
        }

        try:
            res = requests.post(ozonApi.ordersURL, headers=ozonApi.headers(shop), json=payloadOrders)
            if (not res.json()["result"]):
                dateStart = dateEnd
                continue
            # print(payloadOrders)
            # print(res.json())
            print(dateStart.replace(microsecond=0, tzinfo=None))
            print("orders", res.status_code, res.reason)
            ordersInfo["code"].append(res.status_code)
            ordersInfo["reason"].append(res.reason)
            # return

        except Exception as error:
            print(error)
            ordersInfo["code"].append(general.WARNING_CODE)
            ordersInfo["reason"].append(str(error))
            continue

        try:
            orders = pd.json_normalize(res.json(), "result").explode("products", ignore_index=True)
            productsCols = pd.DataFrame.from_records(orders["products"])
            orders[productsCols.columns.values] = productsCols
            deleteCols = orders.columns[5:12].tolist()
            deleteCols.append(orders.columns[-1])
            orders = orders.drop(columns=deleteCols)

            # adding additional info(name of buyer)
            for orderNum in orders["posting_number"]:
                orderAdditionalInfo = getOrderInfo(shop, orderNum)
                if not(orderAdditionalInfo.empty):
                    orders = orders.merge(orderAdditionalInfo, how="left")

            pd.DataFrame(orders.to_excel(ordersDirectory, index=False))
        except Exception as error:
            print(error)
            ordersInfo["code"].append(general.WARNING_CODE)
            ordersInfo["reason"].append(str(error))

        dateStart = dateEnd
        print()

    return organizeData(ordersInfo, general.OK_CODE, "There are no new orders")


# ________________________________________________STATUS________________________________________________________________
def sendStatuses(shop):
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    statusInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": [],
        "reason": []
    }

    files = os.listdir(directories.ozonStatus(shop))
    files = [os.path.join(directories.ozonStatus(shop), file) for file in files]
    for file in sorted(files, key=os.path.getmtime):
        if (not os.path.isfile(file)):
            continue
        print(os.path.basename(file))

        df = pd.read_excel(os.path.join(directories.ozonStatus(shop), file))
        df = df.replace(r'\s+', '', regex=True)
        payload = {}
        shipments = (df.groupby("posting_number")
                     .apply(lambda x: x[x.columns[1:]].to_dict("records"))
                     .reset_index(name="items").reindex(columns=["items", "posting_number"])
                     .to_dict("record"))

        for shipment in shipments:
            payload["packages"] = [{"items": shipment["items"]}]
            payload["posting_number"] = shipment["posting_number"]
            print(payload)

            try:
                res = requests.post(ozonApi.statusURL, headers=ozonApi.headers(shop), json=payload)
                print("Status:", res.status_code, res.reason)
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

    return organizeData(statusInfo, general.OK_CODE, "There are no new status")


# ________________________________________________STOCKS________________________________________________________________
def getProductsList(shop, pageNumber, pageSize):
    payload = {
        "page": pageNumber,
        "page_size": pageSize
    }
    try:
        res = requests.post(ozonApi.productListURL, headers=ozonApi.headers(shop), json=payload)
        print(datetime.datetime.now(pytz.timezone("Europe/Moscow")).replace(microsecond=0, tzinfo=None))
        print("Product lists:", res.status_code, res.reason)
        if (res.status_code != 200):
            print(res.text)
        return res
    except Exception as error:
        print(error)
        return []


def makeDF(res):
    productList = pd.DataFrame.from_records(res.json()["result"]["items"])
    productList = productList.reindex(columns=["offer_id"])
    productList["stock"] = 0
    # print(productList)
    return productList


def sendStocks(shop):
    print(shop)
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    stocksInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": [],
        "reason": []
    }
    # get all products list from ozon
    pageNumber = 1
    pageSize = 1000
    res = getProductsList(shop, pageNumber, pageSize)
    if(res == []):
        stocksInfo["code"] = general.ERROR_CODE
        stocksInfo["reason"] = "Get product list error"
        return stocksInfo
    try:
        total = res.json()["result"]["total"]
        productList = makeDF(res)
        while (total > pageNumber * pageSize):
            pageNumber += 1
            res = getProductsList(shop, pageNumber, pageSize)
            newProductList = makeDF(res)
            # print(newProductList)
            productList = pd.concat([productList, newProductList])
    except Exception as error:
        stocksInfo["code"].append(general.WARNING_CODE)
        stocksInfo["reason"].append(str(error))
        return (stocksInfo)

    productList["warehouse_id"] = 0
    # concat lists
    data = pd.read_excel(directories.ozonStocks(shop) + "ОстаткиОзон.xls")
    data["offer_id"] = data["offer_id"].astype(str)
    data = pd.concat([data, productList]).drop_duplicates("offer_id")

    # list of all products with zero stocks
    allZeroStocks = data[((data["stock"] == 0) & (data["warehouse_id"] == 0))].copy()
    stocksMainWH = data[data["warehouse_id"] == keys.shops[shop]["mainWHID"]].copy()
    stocksDistWH = data[data["warehouse_id"] == keys.shops[shop]["distWHID"]].copy()
    # creat zero stock for products wich have any stock in other warehouse
    # for main warehouse
    zeroStocksForMainWH = stocksDistWH.copy()
    zeroStocksForMainWH["stock"] = 0
    zeroStocksForMainWH["warehouse_id"] = keys.shops[shop]["mainWHID"]
    # for dist warehouse
    zeroStocksForDistWH = stocksMainWH.copy()
    zeroStocksForDistWH["stock"] = 0
    zeroStocksForDistWH = pd.concat([allZeroStocks, zeroStocksForDistWH])
    zeroStocksForDistWH["warehouse_id"] = keys.shops[shop]["distWHID"]
    # add main warehouseID for allZero
    data.loc[((data["stock"] == 0) & (data["warehouse_id"] == 0)), 'warehouse_id'] = keys.shops[shop]["mainWHID"]
    # cocat all df
    data = pd.concat([data, zeroStocksForMainWH, zeroStocksForDistWH])

    # send stocks
    if(data.shape[0] > 100):
        for partData in np.array_split(data, math.ceil(data.shape[0] / 100)):
            data = {"stocks": partData.to_dict(orient='records')}
            try:
                # print(data)
                res = requests.post(ozonApi.stocksURL, headers=ozonApi.headers(shop), json=data)
                print(datetime.datetime.now(pytz.timezone("Europe/Moscow")).replace(microsecond=0, tzinfo=None))
                print("Stocks:", res.status_code, res.reason)
                stocksInfo["code"].append(res.status_code)
                stocksInfo["reason"].append(res.reason)
                if(res.status_code != 200):
                    print(res.text)
            except Exception as error:
                print(error)
                stocksInfo["code"].append(general.WARNING_CODE)
                stocksInfo["reason"].append(str(error))

            print()

    return organizeData(stocksInfo, general.ERROR_CODE, "undefind")


# ______________________________________________PACKAGE_LABLE___________________________________________________________
def getPackageLabel(shop):
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    PLInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": [],
        "reason": []
    }

    postNumFiles = os.listdir(directories.ozonPostingNum(shop))
    postNumFiles = [os.path.join(directories.ozonPostingNum(shop), file) for file in postNumFiles]
    for postNumFile in sorted(postNumFiles, key=os.path.getmtime):
        if (not os.path.isfile(postNumFile)):
            continue
        print(shop)
        print(os.path.basename(postNumFile))

        df = pd.read_excel(postNumFile)
        df = df.replace(r'\s+', '', regex=True)
        payload = df.to_dict("list")
        print(payload)
        try:
            res = requests.post(ozonApi.packageLabelURL, headers=ozonApi.headers(shop), json=payload)
            print(res.status_code, res.reason)
            PLInfo["code"].append(res.status_code)
            PLInfo["reason"].append(res.reason)

            if (res.status_code != 200):
                print(res.text)
                print()
                continue

            with tempfile.TemporaryFile() as pdfMarkFile:
                pdfMarkFile.write(res.content)
                pdfMarkFile.seek(0)
                markImages = convert_from_bytes(pdfMarkFile.read(), poppler_path=directories.poppler_path)
                for i in range(len(markImages)):
                    imageName = payload["posting_number"][i] + '.jpg'
                    markImages[i].save(directories.ozonPackageLabel(shop) + imageName, 'JPEG')

            if (res.status_code == 200):
                os.remove(postNumFile)

        except Exception as error:
            print(error)
            PLInfo["code"].append(general.WARNING_CODE)
            PLInfo["reason"].append(str(error))
        print()

    return organizeData(PLInfo, general.OK_CODE, "There are no new package lable")


# _____________________________________________________ACTS_____________________________________________________________
def savePostingList(shop, WHType, addedPosting):
    deliverList = pd.DataFrame(addedPosting, columns=["posting_number"])
    fileName = "deliverList" + shop + WHType + str(datetime.datetime.today().strftime("%d.%m.%y"))
    pd.DataFrame(deliverList.to_excel(directories.ozonDeliverList(shop) + fileName + ".xls", index=False))
    # safety net
    for i in range(len(addedPosting)):
        deliverDF = pd.DataFrame({"posting_number": [addedPosting[i]]})
        pd.DataFrame(deliverDF.to_excel(
            directories.ozonPostingNum(shop) + fileName + "_" + str(i+1) + ".xls", index=False))


def saveActInJpg(shop, WHType, res):
    imageSettings = {
        "quality": 100,
        "progressive": True,
        "optimize": False
    }

    with tempfile.TemporaryFile() as pdfMarkFile:
        pdfMarkFile.write(res.content)
        pdfMarkFile.seek(0)
        markImages = convert_from_bytes(pdfMarkFile.read(),
                                        dpi=500, fmt="jpeg", jpegopt=imageSettings,
                                        poppler_path=directories.poppler_path)
        for i in range(len(markImages)):
            imageName = str(datetime.datetime.today().strftime("%d.%m.%y")) + "_" + str(i+1) + '.jpg'
            markImages[i].save(directories.ozonActs(shop, WHType) + imageName, 'JPEG')


def saveActInPDF(shop, WHType, res):
    pdfName = shop + WHType + "WH_" + str(datetime.datetime.today().strftime("%d.%m.%y")) + ".pdf"
    with open(directories.ozonAllActs() + pdfName, "wb") as f:
        f.write(res.content)


def getActID(shop, warehouseID):
    print(datetime.datetime.now(pytz.timezone("Europe/Moscow")).replace(microsecond=0, tzinfo=None))
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    actsInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": "",
        "reason": ""
    }
    actID = 0
    try:
        res = requests.post(ozonApi.createActURL,
                            headers=ozonApi.headers(shop), json={"delivery_method_id": warehouseID})
        print("get id", res.status_code, res.reason)
        actsInfo["code"] = res.status_code
        actsInfo["reason"] = res.text
        print(res.text)
        if(res.status_code == 200):
            actID = res.json()["result"]["id"]
        if(res.status_code == 404):
            actsInfo["reason"] = res.json()["message"]
    except Exception as error:
        print(error)
        actsInfo["code"] = general.WARNING_CODE
        actsInfo["reason"] = str(error)
    finally:
        return actID, actsInfo


def readinessAct(shop, WHType, actID):
    print(datetime.datetime.now(pytz.timezone("Europe/Moscow")).replace(microsecond=0, tzinfo=None))
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    actsInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": "",
        "reason": ""
    }
    readiness = False
    try:
        res = requests.post(ozonApi.actStatusURL, headers=ozonApi.headers(shop), json={"id": actID})
        actsInfo["code"] = res.status_code
        actsInfo["reason"] = res.json()["result"]["status"].capitalize()
        print("check status", res.status_code, res.reason)
        print(res.json())
        if(res.json()["result"]["status"] == "ready"):
            readiness = True
            addedPosting = res.json()["result"]["added_to_act"]
            savePostingList(shop, WHType, addedPosting)
    except Exception as error:
        print(error)
        actsInfo["code"] = general.WARNING_CODE
        actsInfo["reason"] = error
    finally:
        return readiness, actsInfo


def getAct(shop, WHType, actID):
    print(datetime.datetime.now(pytz.timezone("Europe/Moscow")).replace(microsecond=0, tzinfo=None))
    datetimeMSK = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    actsInfo = {
        "time": datetimeMSK.strftime("%d.%m.%y %H:%M:%S"),
        "code": "",
        "reason": ""
    }
    try:
        res = requests.post(ozonApi.getActURL, headers=ozonApi.headers(shop), json={"id": actID})
        print("get acts", res.status_code, res.reason)
        actsInfo["code"] = res.status_code
        actsInfo["reason"] = res.reason
        if (res.status_code == 200):
            # saveActInJpg(shop, WHType, res)
            saveActInPDF(shop, WHType, res)
            actsInfo["code"] = general.OK_CODE
            actsInfo["reason"] = "Saved"
    except Exception as error:
        actsInfo["code"] = general.WARNING_CODE
        actsInfo["reason"] = str(error)
        print(error)
    finally:
        return actsInfo
