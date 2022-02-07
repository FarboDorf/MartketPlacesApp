import os


class Path:
    def __init__(self):
        self.base_path = r"\\server2020\Общая\MarketplaceExchange"

    # WB
    def WBOrders(self, shop) -> str:
        if(shop == "Fortuna"):
            return self.base_path + r"\WB\fromWB\\"
        else:
            return self.base_path + r"\\" + shop + r"\WB" + shop + r"\fromWB\\"

    # @property
    # def WBStatus(self) -> str:
    #     return self.base_path + r"\WB\toWB\WBStatus\\"

    def WBStatus(self, shop) -> str:
        if(shop == "Fortuna"):
            return self.base_path + r"\WB\toWB\WBStatus\\"
        else:
            return self.base_path + r"\Progress\WBProgress\toWB\WBStatus"

    def WBStocks(self, shop) -> str:
        if (shop == "Fortuna"):
            return self.base_path + r"\WB\toWB\WBStocks\\"
        else:
            return self.base_path + r"\\" + shop + r"\WB" + shop + r"\toWB\WBStocks\\"

    def WBBarcodes(self, shop) -> str:
        if (shop == "Fortuna"):
            return self.base_path + r"\WB\fromWB\barcodes\\"
        else:
            return self.base_path + r"\\" + shop + r"\WB" + shop + r"\fromWB\barcodes\\"

    def WBOrderList(self, shop) -> str:
        if (shop == "Fortuna"):
            return self.base_path + r"\WB\toWB\WBOrderList"
        else:
            return self.base_path + r"\\" + shop + r"\WB" + shop + r"\toWB\WBOrderList"

    def WBCloseSupply(self, shop) -> str:
        if (shop == "Fortuna"):
            return self.base_path + r"\WB\toWB\WBCloseSupply"
        else:
            return self.base_path + r"\\" + shop + r"\WB" + shop + r"\toWB\WBCloseSupply"

    def WBSupplyList(self, shop) -> str:
        if(shop == "Fortuna"):
            return self.base_path + r"\WB\toWB\WBSuppliesList\\"
        else:
            return self.base_path + r"\\" + shop + r"\WB" + shop + r"\toWB\WBSuppliesList\\"

    def WBSupplyOrdersCnt(self):
        return self.base_path + r"\WB\fromWB\supplyOrderCount\\"

    def WBSupplyBarcode(self, shop) -> str:
        return self.base_path + r"\WB\fromWB\supplyBarcode\\"

    def WBLogs(self, shop) -> str:
        if (shop == "Fortuna"):
            return self.base_path + r"\WB\logs\\"
        else:
            return self.base_path + r"\\" + shop + r"\WB" + shop + r"\logs\\"

    # OZON
    def ozonOrders(self, shop) -> str:
        if (shop == "Fortuna"):
            return self.base_path + r"\Ozon\fromOzon\\"
        else:
            return self.base_path + r"\\" + shop + r"\Ozon" + shop + r"\fromOzon\\"

    def ozonStatus(self, shop) -> str:
        if (shop == "Fortuna"):
            return self.base_path + r"\Ozon\toOzon\OzonStatus\\"
        else:
            return self.base_path + r"\\" + shop + r"\Ozon" + shop + r"\toOzon\OzonStatus\\"

    def ozonStocks(self, shop) -> str:
        if (shop == "Fortuna"):
            return self.base_path + r"\Ozon\toOzon\OzonStocks\\"
        else:
            return self.base_path + r"\\" + shop + r"\Ozon" + shop + r"\toOzon\OzonStocks\\"

    def ozonPackageLabel(self, shop) -> str:

        return self.base_path + r"\Ozon\fromOzon\OzonPackageLabel\\"

        if (shop == "Fortuna"):
            return self.base_path + r"\Ozon\fromOzon\OzonPackageLabel\\"
        else:
            return self.base_path + r"\\" + shop + r"\Ozon" + shop + r"\fromOzon\OzonPackageLabel\\"

    def ozonActs(self, shop, WHType) -> str:
        if(WHType == "ozonActsMainWH"):
            subfolder = "MainWarehouse"
        elif(WHType == "ozonActsDistWH"):
            subfolder = "DistWarehouse"

        return self.base_path + r"\Ozon\fromOzon\OzonActs\\" + subfolder + r"\\"

        if (shop == "Fortuna"):
            return self.base_path + r"\Ozon\fromOzon\OzonActs\\" + subfolder + r"\\"
        else:
            return self.base_path + r"\\" + shop + r"\Ozon" + shop + r"\fromOzon\OzonActs\\" + subfolder + r"\\"

    def ozonAllActs(self):
        return self.base_path + r"\Ozon\fromOzon\OzonAllActs\\"

    def ozonDeliverList(self, shop) -> str:

        return self.base_path + r"\Ozon\fromOzon\OzonDeliverList\\"

        if (shop == "Fortuna"):
            return self.base_path + r"\Ozon\fromOzon\OzonDeliverList\\"
        else:
            return self.base_path + r"\\" + shop + r"\Ozon" + shop + r"\fromOzon\OzonDeliverList\\"

    def ozonPostingNum(self, shop) -> str:
        if (shop == "Fortuna"):
            return self.base_path + r"\Ozon\toOzon\OzonPostingNum\\"
        else:
            return self.base_path + r"\\" + shop + r"\Ozon" + shop + r"\toOzon\OzonPostingNum\\"

    @property
    def poppler_path(self) -> str:
        return os.path.normpath(os.path.join(os.path.abspath(os.path.curdir), "poppler-0.68.0", "bin"))
