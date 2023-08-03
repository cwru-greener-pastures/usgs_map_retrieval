#!/usr/bin/env python

import os, json, yaml
from PIL import Image, ImageDraw

from osgeo import osr

class BuildFootprints(object):
    def __init__(self, map_config_file):

        if not os.path.exists(map_config_file):
            raise FileNotFoundError


        # Load map configurations
        map_config_h = open(map_config_file)
        map_config_txt = map_config_h.read()
        map_config_h.close()
        map_config = yaml.safe_load(map_config_txt)

        # Load building foortprints data
        buildings_h = open(map_config['map_json'])
        buildings_txt = buildings_h.read()
        buildings_h.close()
        building_footprints = json.loads(buildings_txt)

        # Setup transformations for footprint coordinates
        source = osr.SpatialReference()
        source.ImportFromEPSG(building_footprints['queryGeometry']['spatialReference']['latestWkid'])
        # This is the coordinate reference system that should be in meters
        target = osr.SpatialReference()
        target.ImportFromEPSG(3857)

        # Create a transform between the two reference frames
        transform = osr.CoordinateTransformation(source, target)

        offset = [float('inf'), float('inf')]
        for ring in building_footprints['queryGeometry']['rings'][0]:
            offset = [min(ring[0], offset[0]), min(ring[1], offset[1])]
        offset = map_config['origin']

        # Get size and resolution of the map to produce from the map_config
        image_size = map_config['size']
        reso = map_config['resolution']

        # Initialize an image and polygon drawing interface
        im = Image.new('L', [image_size, image_size], 255)
        im_d =ImageDraw.Draw(im)

        # For each building
        for building in building_footprints['features']:

            # These are polygons, find each identified point
            fp = []
            # new_point = []
            for coord in building['geometry']['rings'][0]:
                # For each point, convert it to image coordinates from local coordinates
                # This is where transformations should occur.  Below is just an example.
                # new_point.append(transform.TransformPoint(coord[0], coord[1]))
                fp.append(tuple([int(max(0, min(coord[0] - offset[0], image_size))) / reso, 
                            int(max(0, image_size - min(coord[1] - offset[1], image_size))) / reso]))

            # Draw the polygon on the image
            im_d.polygon(fp, 0)

        # Save the image
        im.save(map_config['image'])

        # Close the image
        im.close()


if __name__ =='__main__':
    BF = BuildFootprints('config/footprints.yaml')