from datetime import datetime, date


def convertToMonth(date_str):
    date = datetime.strptime(str(date_str), "%Y-%m-%d")
    return date.strftime("%B, %Y")

v = convertToMonth("2023-10-01")
print(v)

