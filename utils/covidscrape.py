import requests

def get_covid_data(countryname="Global"):
  r = requests.get('https://api.covid19api.com/summary')
  if r.status_code == 404:
    print("The resource you tried to access wasn’t found on the server.")
    
  elif r.status_code == 403:
    print("the resource you’re trying to access is forbidden — you don’t have the right permissions to see it.")
    
  elif r.status_code == 400:
    print("Bad Request")
    
  elif r.status_code == 401:
    print("Not Authenticated")
    
  elif r.status_code == 301:
    print("Switching to a different endpoint")
    
  elif r.status_code == 200:
    if countryname == "Global":
      dat = r.json()
      return dat['Global']
    else:
      data = r.json()['Countries']
      found = False

      for country in data:
        if country['Country'].lower() == countryname.lower():
          # print(f"Country : {country['Country']}")
          # print(f"New Confirmed : {country['NewConfirmed']}")
          # print(f"Total Confirmed : {country['TotalConfirmed']}")
          # print(f"New Deaths : {country['NewDeaths']}")
          # print(f"Total Deaths : {country['TotalDeaths']}")
          # print(f"New Recovered : {country['NewRecovered']}")
          # print(f"Total Recovered : {country['TotalRecovered']}")
          return country
          found = True
          break

      if not found:
        print('Country Not Found!')
        return False

