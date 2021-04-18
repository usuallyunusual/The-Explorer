import urllib.request,urllib.parse,urllib.error
import json
import ssl
def get_loc(country):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    api_key = 42
    serviceurl = 'http://py4e-data.dr-chuck.net/json?'


    param = country
    url = serviceurl + urllib.parse.urlencode({"address":param,"key":api_key})
    #print("Retrieving",url)
    text = urllib.request.urlopen(url,context = ctx).read().decode()
    #print("Retrieved",len(text),"characters")
    try:
    	js = json.loads(text)
    except:
    	js = None

    if not js or 'status' not in js or js['status'] != 'OK':
            print('==== Failure To Retrieve ====')
            print(text)
            quit()
    #print("Place id",js["results"][0]["place_id"])
    return(js["results"][0]["geometry"]["location"])

