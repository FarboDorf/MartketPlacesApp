from collections import Counter


OK_CODE = 200
WARNING_CODE = 600
ERROR_CODE = 999


def organizeData(data, altCode, altReason):
    if (data["code"]):
        # print(Counter(statusInfo["code"]))
        data["code"] = str(max(Counter(data["code"]), key=Counter(data["code"]).get))
        reasonsStr = ""
        for key, val in Counter(data["reason"]).most_common():
            reasonsStr += str(key) + " - " + str(val) + "; "
        data["reason"] = reasonsStr
    else:
        data["code"] = altCode
        data["reason"] = altReason

    return data
