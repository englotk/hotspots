import simplekml
import zipfile
from random import uniform
from math import log
from io import BytesIO
from urllib.parse import urlparse, unquote
from http.server import BaseHTTPRequestHandler
from hotspot_api import download_hotspots

def gethotspots(lng,lat,distance,tsa=0.8,tsi=0,isa=0.8,isi=0.5,ica=None,ici='ff0000ff'):
    kml=simplekml.Kml(name='Hotspots')
    jsondata=download_hotspots(lng,lat,distance)

    count=0
    noloccount=0
    for hotspot in jsondata:

        #addr=str(hotspot['address'])
        #block_added=str(hotspot['block_added'])
        #location = str(hotspot['location'])
        #country = str(hotspot['geocode']['short_country'])
        elevation=int(hotspot['elevation'])
        gain=int(hotspot['gain'])
        online=str(hotspot['status']['online'])

        pnt = kml.newpoint(name=hotspot['name'], coords=[(hotspot['lng'],hotspot['lat'])])

        if online == 'online': # active
            pnt.style.labelstyle.scale=tsa
            pnt.style.iconstyle.scale = isa
            if ica != '':
                pnt.style.iconstyle.color=ica
        else:   # inactive
            pnt.style.iconstyle.scale = isi
            pnt.style.labelstyle.scale=tsi
            pnt.style.iconstyle.color = ici # Red

        pnt.extendeddata.newdata(name='Scaling', value=hotspot["reward_scale"], displayname='Scaling from API')
        pnt.extendeddata.newdata(name='Online', value=online, displayname='Online')
        pnt.extendeddata.newdata(name='Gain', value=gain, displayname='Antenna Gain')
        pnt.extendeddata.newdata(name='Elevation', value=elevation, displayname='Antenna Elevation')
            
    #print(kml.kml())
    return kml.kml(format=False)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print('GET')
        self.send_response(200)
        #self.send_header('Content-type', 'text/plain')
        self.send_header('Content-type', 'application/vnd.google-earth.kmz')
        #self.send_header('Content-type', 'application/vnd.google-earth.kml+xml')
        self.end_headers()

        print(self.path)
        query = urlparse(self.path).query
        query=unquote(query)

        bbox,alt,tsa,tsi,isa,isi,ica,ici,dis=query.split(';')

        # get the altitude of the camera
        alt = float(alt.split('CAMERA=')[1])
        west,south,east,north=bbox.split('BBOX=')[1].split(',')
    
        # find the center of the map and the altitude
        west = float(west)
        south = float(south)
        east = float(east)
        north = float(north)

        lng = ((east - west) / 2) + west
        lat = ((north - south) / 2) + south
        tsa = float(tsa.split('TSA=')[1])
        tsi = float(tsi.split('TSI=')[1])
        isa = float(isa.split('ISA=')[1])
        isi = float(isi.split('ISI=')[1])
        ica = str(ica.split('ICA=')[1])
        ici = str(ici.split('ICI=')[1])
        dis = int(dis.split('DIS=')[1])

        hotspots=gethotspots(lat=lat,lng=lng,distance=int(alt+dis),tsa=tsa,tsi=tsi,isa=isa,isi=isi,ica=ica,ici=ici)

        # send the new kml back to google earth
        #print("before",len(hotspots))

        in_memory_zip = BytesIO()

        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)
        #zf = zipfile.ZipFile(in_memory_zip, "w")

        zf.writestr('hotspots.kml', hotspots)
        zf.close()   
        #print('after',len(in_memory_zip.getvalue()))
        self.wfile.write(in_memory_zip.getvalue())
        return

