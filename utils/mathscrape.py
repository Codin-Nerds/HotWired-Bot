import requests


def get_math_results(equation: str) -> str:
    """Use `api.mathjs.org` to calculate any given equation"""
    params = {"expr": equation}
    url = "http://api.mathjs.org/v4/"
    r = requests.get(url, params=params)

    if r.status_code == 200:
        return r.text
    elif r.status_code == 404:
        return "The resource you tried to access wasn’t found on the server."
    elif r.status_code == 403:
        return "the resource you’re trying to access is forbidden — you don’t have the right permissions to see it."
    elif r.status_code == 400:
        return "Bad Request"
    elif r.status_code == 401:
        return "Not Authenticated"
    elif r.status_code == 301:
        return "Switching to a different endpoint"
    return "Invalid Equation"
