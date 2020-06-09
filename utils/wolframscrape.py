import requests

APPID = "E75JHH-HAUP4AYJTT"

def get_wolfram_data(question, conversation_mode="false", units="metric"):
  if conversation_mode.lower() == "yes" or conversation_mode.lower() == "true":
    params = {
      'appid': APPID,
      'i': question,
      'units': units
    }
    url = 'http://api.wolframalpha.com/v1/conversation.jsp'
    r = requests.get(url, params=params)
    data = r.json()['result']

    return data

  else:
    params = {
      'appid': APPID,
      'i': question,
      'units': units
    }
    url = 'http://api.wolframalpha.com/v1/result'
    r = requests.get(url, params=params)
    data = r.text

    return data
