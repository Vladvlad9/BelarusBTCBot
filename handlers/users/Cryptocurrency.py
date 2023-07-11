import requests
from fake_useragent import UserAgent


class Cryptocurrency:

    @staticmethod
    async def get_byn() -> float:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }

        get_request = requests.get(url="https://www.nbrb.by/api/exrates/rates/431", headers=headers)
        try:
            if get_request.status_code == 200:
                data = get_request.json()
                price = float(data["Cur_OfficialRate"])
                return price
            else:
                print(get_request.status_code)
        except Exception as e:
            print(e)

    @staticmethod
    async def get_rub() -> float:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }

        try:
            url: str = f"https://www.binance.com/api/v1/aggTrades?limit=1&symbol=USDTRUB"
            get_request = requests.get(url=url, headers=headers)

            if get_request.status_code == 200:
                data = get_request.json()
                price: float = float(data[0]['p'])
                return price
            else:
                print(get_request.status_code)
        except Exception as e:
            print(e)

    @staticmethod
    async def get_btc() -> float:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }

        try:
            url: str = f"https://www.binance.com/api/v1/aggTrades?limit=1&symbol=BTCUSDT"
            get_request = requests.get(url=url, headers=headers)

            if get_request.status_code == 200:
                data = get_request.json()
                price: float = float(data[0]['p'])
                return price
            else:
                print(get_request.status_code)
        except Exception as e:
            print(e)



