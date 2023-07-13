import logging

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
                logging.error(f'Error status code get_bun: {get_request.status_code}')
        except Exception as e:
            logging.error(f'Error transfer get_bun: {e}')

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
                logging.error(f'Error status code get_rub: {get_request.status_code}')
        except Exception as e:
            logging.error(f'Error transfer get_rub: {e}')

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
                logging.error(f'Error status code get_btc: {get_request.status_code}')
        except Exception as e:
            logging.error(f'Error transfer get_btc: {e}')

    @staticmethod
    async def get_ltc() -> float:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }

        try:
            url: str = f"https://www.binance.com/api/v1/aggTrades?limit=1&symbol=LTCUSDT"
            get_request = requests.get(url=url, headers=headers)

            if get_request.status_code == 200:
                data = get_request.json()
                price: float = float(data[0]['p'])
                return price
            else:
                logging.error(f'Error status code get_ltc: {get_request.status_code}')
        except Exception as e:
            logging.error(f'Error transfer get_ltc: {e}')

    @staticmethod
    async def get_trx() -> float:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }

        try:
            url: str = f"https://www.binance.com/api/v1/aggTrades?limit=1&symbol=TRXUSDT"
            get_request = requests.get(url=url, headers=headers)

            if get_request.status_code == 200:
                data = get_request.json()
                price: float = float(data[0]['p'])
                return price
            else:
                logging.error(f'Error status code get_trx: {get_request.status_code}')
        except Exception as e:
            logging.error(f'Error transfer get_trx: {e}')

    @staticmethod
    async def get_xmr() -> float:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }

        try:
            url: str = f"https://www.binance.com/api/v1/aggTrades?limit=1&symbol=XMRUSDT"
            get_request = requests.get(url=url, headers=headers)

            if get_request.status_code == 200:
                data = get_request.json()
                price: float = float(data[0]['p'])
                return price
            else:
                logging.error(f'Error status code get_xmr: {get_request.status_code}')
        except Exception as e:
            logging.error(f'Error transfer get_xmr: {e}')

    @staticmethod
    async def get_ltc_to_rub() -> float:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }

        try:
            url: str = f"https://www.binance.com/api/v1/aggTrades?limit=1&symbol=LTCRUB"
            get_request = requests.get(url=url, headers=headers)

            if get_request.status_code == 200:
                data = get_request.json()
                price: float = float(data[0]['p'])
                return price
            else:
                logging.error(f'Error status code ltc to rub: {get_request.status_code}')
        except Exception as e:
            logging.error(f'Error transfer ltc to rub: {e}')

    @staticmethod
    async def Check_Wallet(btc_address: str) -> bool:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        # http://45.155.203.112:8000
        proxies = {
            'http': 'http://45.155.203.112:8000'
        }

        try:
            url = f'https://blockchain.info/q/addressbalance/{btc_address}'

            get_url = requests.get(url=url, headers=headers)
            if get_url.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            logging.error(f'Error Check_Wallet: {e}')
            return False




