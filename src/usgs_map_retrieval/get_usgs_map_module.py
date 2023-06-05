#!/usr/bin/env python

import math, os, json, yaml, base64

import urllib.parse, urllib.request, urllib.error

from osgeo import osr

class GetUSGSMap(object):

    def GetMap(self, request_url, request_json, filename, just_json=False):

        # Create the full URL request to retrieve the map data.
        requrl = request_url + '?' + urllib.parse.urlencode(request_json)

        # Just return the full URL request text.
        if just_json:
            return(requrl)

        # Break apart the filename to use for saving the map and possibly other data.
        pname, fname = os.path.split(filename)
        fname, ename = os.path.splitext(fname)

        # Use the format specification to create a file extension
        if (request_json['format'] == 'tiff'):
            ename = 'tif'
        elif (request_json['format'] == 'jpgpng'):
            ename = 'png'
        elif('png' in request_json['format']):
            ename = 'png'
        else:
            ename = request_json['format']

        try:
            if (request_json['f'] == 'json'):
                # If the 'f' field is for a JSON response, capture the data and save it all
                url_ret_raw = urllib.request.urlopen(requrl)
                url_ret = json.loads(url_ret_raw.read())

                # There have been two types of responses to JSON requests.  
                # This one is not documented, the image data is in a field of the response
                try:
                    ret_data = base64.b64decode(url_ret.pop('imageData'))
                    url_ret.pop('contentType')
                except:
                    pass

                # Save the JSON data into a YAML file so that it can be loaded into the Parameter Server if desired/required.
                out = open(os.path.join(pname, fname + os.path.extsep + 'yaml'), 'w+')
                out.write(yaml.safe_dump(url_ret, indent=4, sort_keys=False))
                out.close()

                #  If there is a link to the image data, get it.
                #  This is the documented way it should work.
                if ('href' in url_ret):
                    requrl = url_ret['href']
                    ret = urllib.request.urlopen(requrl, url_ret_raw)
                    ret_data = ret.read()

            elif(request_json['f'] == 'image'):
                # This method sends the raw image map file data only.
                ret = urllib.request.urlopen(requrl)
                ret_data = ret.read()

            # Write the raw image data to the file.
            out = open(os.path.join(pname, fname + os.path.extsep + ename), 'wb')
            out.write(ret_data)
            out.close()

            return(0)

        except urllib.error.URLError as e:
            print('Fetch from %s failed: %s' % (request_url, e.reason))
        except OSError as e:
            print('File problem with %s: %s' % (filename, e.args[0]))
        except Exception as e:
            print('Fetch failed: %s' % (e.args[0]))

        return (-1)

    def getBboxFromWGS84(self, coord_x, coord_y, coord_SR, siz, request_SR=3857):

        # This is the typical GPS coordinate reference system (WGS 84/EPSG:4326)
        source = osr.SpatialReference()
        source.ImportFromEPSG(coord_SR)

        # This is the coordinate reference system the servers accept
        target = osr.SpatialReference()
        target.ImportFromEPSG(request_SR)

        # Create a transform between the two reference frames
        transform = osr.CoordinateTransformation(source, target)
        
        # Transform the input coordinates
        ret = tuple(map(math.floor, transform.TransformPoint(coord_x, coord_y)))

        return(ret[0] + math.ceil(siz/2), ret[1] + math.floor(siz/2), ret[0] - math.ceil(siz/2) , ret[1] - math.floor(siz/2))
