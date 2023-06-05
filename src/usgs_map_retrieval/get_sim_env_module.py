#!/usr/bin/env python

import math, os, re, statistics

from osgeo import osr, gdal

world_file = 'usgs_simulation_environment.world'

world_template = '''<?xml version="1.0" ?> 
<sdf version="1.5">
  <world name="USGS 3DEPElevation/NAIP World">
    <scene>
      <sky>
        <clouds>
          <speed>2</speed>
        </clouds>
      </sky>
    </scene>
    <!-- A global light source -->
    <include>
      <uri>model://sun</uri>
    </include>
    <model name="terrain">
      <static>true</static>
      <link name="terrain_link">
        <collision name="terrain_collision">
          <geometry>
            <heightmap>
              <use_terrain_paging>false</use_terrain_paging>
              <uri>file://worlds/heightmap.tif</uri>
              <pos>0 0 0</pos>
            </heightmap>
          </geometry>
        </collision>
        <visual name="terrain_visual">
          <geometry>
            <heightmap>
              <use_terrain_paging>false</use_terrain_paging>
              <texture>
                <diffuse>file://worlds/texture.png</diffuse>
                <size>1028</size>
                <normal>file://media/materials/textures/flat_normal.png</normal>
              </texture>
              <uri>file://worlds/heightmap.tif</uri>
              <pos>0 0 0</pos>
            </heightmap>
          </geometry>
        </visual>
      </link>
    </model>
  </world>
</sdf>
'''

# This class simplifies updates to the world file
class WorldFileUpdate(object):
    def __init__(self, filename=world_file, directory='') -> None:
        self.world_file = filename
        self._directory =  directory

    def setHeightmapOffset(self, heightmap_name):
        # Load the heightmap data to calculate the height of the heightmap at the center
        hm_data = gdal.Open(heightmap_name)
        raw_data = hm_data.ReadAsArray()
        offset = statistics.mean((raw_data[math.floor(hm_data.RasterXSize / 2), math.floor(hm_data.RasterYSize / 2)],
                                raw_data[math.floor(hm_data.RasterXSize / 2), math.ceil(hm_data.RasterYSize / 2)],
                                raw_data[math.ceil(hm_data.RasterXSize / 2), math.floor(hm_data.RasterYSize / 2)],
                                raw_data[math.ceil(hm_data.RasterXSize / 2), math.ceil(hm_data.RasterYSize / 2)]))

        world_data = self.openWorldFile()
        # Move the surface of the heightmap to intersect the origin of the Gazebo environment        
        world_data = re.sub(r'(<pos>[ ]*[+|-]?[.\d]+\s+[+|-]?[.\d]+\s+)[+|-]?[.\d]+(\s*</pos>)', r'\g<1>%f\2' % (-offset), world_data)

        self.closeWorldFile(world_data)

    def setTextureScale(self, texture_scale=0, heightmap_name=''):

        # # Calculate the scale for the texture map based on the heightmap
        if (os.path.exists(heightmap_name) and (texture_scale == 0)):
            hm_data = gdal.Open(heightmap_name)
            transform = self.getTransform(4326, 3857)
            geotrans = hm_data.GetGeoTransform()
            lon = (geotrans[3] + hm_data.RasterXSize/2 * geotrans[5], geotrans[3] - hm_data.RasterXSize/2 * geotrans[5])
            lat = (geotrans[0] + hm_data.RasterXSize/2 * geotrans[1], geotrans[0] - hm_data.RasterXSize/2 * geotrans[1])
            p1 = transform.TransformPoint(lon[0], lat[0])
            p2 = transform.TransformPoint(lon[0], lat[1])
            texture_scale = int(math.fabs(p2[0] - p1[0]))

        world_data = self.openWorldFile()
        # Scale the texture to fit the heightmap
        world_data = re.sub(r'(<size>)\s*[.\d]*\s*(</size>)', r'\g<1>%i\2' % (texture_scale), world_data)
        self.closeWorldFile(world_data)

    def setTextureFiletype(self, textureFilename):
        world_data = self.openWorldFile()

        world_data = re.sub(r'(<diffuse>)\S*(</diffuse>)', r'\g<1>file://worlds/%s\2' % (os.path.split(textureFilename)[1]), world_data)

        self.closeWorldFile(world_data)

    def openWorldFile(self):
        world_file = os.path.join(self._directory, self.world_file)
        # Update the .world file so that heightmap intersection the Gazebo origin, and the texture scale is correct
        if (os.path.exists(world_file)):
            # If the file exists, read it in (so as to leave other alterations unchanged)
            self._inp = open(world_file, 'r+')
            world_data = self._inp.read()
        else:
            # Creat the file if it does not exist and use a template
            self._inp = open(world_file, 'w+')
            world_data = world_template

        return(world_data)
    
    def closeWorldFile(self, world_data):
        # If the file existed and was read, move the marker back to the beginning and empty it
        self._inp.seek(0)
        self._inp.truncate(0)
        self._inp.write(world_data)
        self._inp.close()

    def getTransform(self, coord_SR, request_SR):
        # This is the typical GPS coordinate reference system (WGS 84/EPSG:4326)
        source = osr.SpatialReference()
        source.ImportFromEPSG(coord_SR)

        # This is the coordinate reference system the servers accept
        target = osr.SpatialReference()
        target.ImportFromEPSG(request_SR)

        # Create a transform between the two reference frames
        return(osr.CoordinateTransformation(source, target))



if __name__ =='__main__':
  pass