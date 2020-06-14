import requests
import setup

APPID = setup.WOLFRAM_APPID


def get_wolfram_data(question: str, conversation_mode: str = "false", units: str = "metric") -> str:
    if conversation_mode.lower() == "yes" or conversation_mode.lower() == "true":
        params = {"appid": APPID, "i": question, "units": units}
        url = "http://api.wolframalpha.com/v1/conversation.jsp"
        r = requests.get(url, params=params)
        data = r.json()["result"]

        return data

    else:
        params = {"appid": APPID, "i": question, "units": units}
        url = "http://api.wolframalpha.com/v1/result"
        r = requests.get(url, params=params)
        data = r.text

        return data
