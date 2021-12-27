import requests
import json

headers = {
    'User-Agent': 'INSERT_VALID_HEADER_HERE',
    'From': 'your@email.com'  # This is another valid field
}

def download_hotspots(lng=0.0,lat=0.0,distance=100):
    # using the helium api this function downloads hotspots from current GE view
    params='lat='+str(lat)+'&lon='+str(lng)+'&distance='+str(distance)
    url = "https://api.helium.io/v1/hotspots/location/distance?"+params
    #print(url)
    data=requests.get(url=url, headers=headers)
    data=data.json()

    # check if there is more than 1 page of hotspots
    try:
        cursor = data['cursor']
    except KeyError:
        cursor=None

    data = data['data']
    jsondata=data
    
    #print('Getting hotspots from api')
    while(cursor):
        
        data=requests.get(url=url+params+'&cursor='+cursor, headers=headers)
        data=data.json()

        try:
            cursor = data['cursor']
        except KeyError:
            cursor=None
        data = data['data']
        jsondata=jsondata+data

    return jsondata

if __name__ == '__main__':
    download_hotspots()
