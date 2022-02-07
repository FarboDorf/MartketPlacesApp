import keys


class OzonApi:
    def __init__(self):
        self.base_url = "https://api-seller.ozon.ru"

    @staticmethod
    def headers(shop) -> dict:
        headers = {"Client-Id": keys.shops[shop]["ozonClientID"],
                   "Content-Type": "application/json",
                   "Api-Key": keys.shops[shop]["ozonToken"]
                   }
        return headers

    @property
    def ordersURL(self) -> str:
        return self.base_url + "/v2/posting/fbs/list"

    @property
    def ordersInfoURL(self) -> str:
        return self.base_url + "/v3/posting/fbs/get"

    @property
    def statusURL(self) -> str:
        return self.base_url + "/v2/posting/fbs/ship"

    @property
    def productListURL(self) -> str:
        return self.base_url + "/v1/product/list"

    @property
    def stocksURL(self) -> str:
        return self.base_url + "/v2/products/stocks"

    @property
    def packageLabelURL(self) -> str:
        return self.base_url + "/v2/posting/fbs/package-label"

    @property
    def createActURL(self) -> str:
        return self.base_url + "/v2/posting/fbs/act/create"

    @property
    def actStatusURL(self) -> str:
        return self.base_url + "/v2/posting/fbs/act/check-status"

    @property
    def getActURL(self) -> str:
        return self.base_url + "/v2/posting/fbs/act/get-pdf"


class WBApi:
    def __init__(self):
        self.base_url = "https://suppliers-api.wildberries.ru/api"

    @staticmethod
    def headers(shop) -> dict:
        return {"Authorization": keys.shops[shop]["WBTokenV2"]}

    @property
    def baseOrdersURL(self) -> str:
        return self.base_url + "/v2/orders?date_start="

    @property
    def statusURL(self) -> str:
        return self.base_url + "/v2/orders"

    @property
    def supplyIdURL(self) -> str:
        return self.base_url + "/v2/supplies"

    def addSupplyURL(self, supplyId) -> str:
        return self.base_url + "/v2/supplies/" + supplyId

    def closeSupplyURL(self, supplyId) -> str:
        return self.base_url + "/v2/supplies/" + supplyId + "/close"

    def supplyBarcodeURL(self, supplyId) -> str:
        return self.base_url + "/v2/supplies/" + supplyId + "/barcode"

    def supplyOrdersURL(self, supplyId) -> str:
        return self.base_url + "/v2/supplies/" + supplyId + "/orders"

    @property
    def stocksURL(self) -> str:
        return self.base_url + "/v2/stocks"

    @property
    def stickersURL(self) -> str:
        return self.base_url + "/v2/orders/stickers"
