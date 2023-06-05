# The `usgs_map_retrieval` package

The `usgs_map_retrieval` package was developed as part of the **Greener Pastures** project with support from a Grand from the USDA-NIFA/NSF-CPS programs, Award Number 2021-67021-34459, and is published for public use.

## Introduction
This package facilitates the retrieval of data from the USGS for use with robots.  The USGS data can be used to create a ROS/Gazebo simulation environment, or to develop maps for navigation.

This project connects to those servers using the ArGIS REST protocol at the following servers:

> [USGS 3DPEPElevation ArcGIS REST Server](https://elevation.nationalmap.gov/arcgis/rest/services) for `heightmap`, `aspect`, and `slope` maps.
>
> [USGS NAIP Plus ArcGIS REST Server](https://imagery.nationalmap.gov/arcgis/rest/services) for `texture` images.
>
> [USGS Transportation Service](https://carto.nationalmap.gov/arcgis/rest/services) for transportation (`roads`) maps.
>
> [USGS Rendering of US Fish & Wildlife Weland Maps](https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services) for `wetland` maps.

## Navigation Maps

Maps useful for navigation can be retrieved from several USGS services.  Maps that contain

- Slope of environment
- Aspect of slope of enviroment
- Location of roads
- Location of wetlands
- ~~Building footprints~~  Not currently implemented

The location of the map can be specified in WGS84 longitude/latitdude which is Coordinate Reference System (CRS) used by GPS devices and Google Maps.  (It is possibel to right click on a Google Map to inspect longitude and latitude.)

### Usage

All available maps can be retrieved using the following command:

> `rosrun usgs_map_retrieval get_maps <`*`longitude`*`> <`*`latitude`*`>`

It is possible to retrieve specific maps using the following command:

> `rosrun usgs_map_retrieval get_maps <`*`longitude`*`> <`*`latitude`*`> -m <aspect|slope|roads|wetlands>`

A `map-server` compatible configuration yaml is generated for each map during this process.

All files are saved to the `config` directory of the `usgs_map_retrieval` package if run in ROS, or in the Current Working Directory if run without ROS.

## ROS/Gazebo Simulation

**Gazebo has an unidentified memory issue that will cause it to crash when changing the `heightmap` and/or `texture` files.  One bug that causes a crash is that Gazebo uses `terrain_paging` is spite of the `.world` file containing the configuration to prevent it.  Preventing this requires deleting the `~/.gazebo/paging/heightmap*/` directory associated with the `heightmap` file.  There is also some memory issue that will continue to cause Gazebo to crash after removing the `terrain_paging` directory.  It seems that waiting an extended period of time (5-10 minutes) before invoking Gazebo again results in success.**

The package creates files necessary to for a ROS/Gazebo simulation at desired WGS84 longitude/latitude coordinates.  (WGS84 coordinates are typical GPS or Google Maps Longitude and Latitude coordinates.)  `heightmap`s and `texture`s are downloaded from the National Map published by the USGS where data from the 3D Elevation Program (3DEP) and the National Agricultural Imaging Project Plus (NAIP Plus) Images are provided to the public.  It also creates a `.world` file in `SDF` format for use with Gazebo.

### Usage

#### Retrieving Elevation and Imagery Data

Image files use for `heightmap` and `texture` for Gazebo simulation can be retrieved from the USGS based on the longitude/latitude coordinates of the center of the region desired.  It is possible to right on a Google Map or use the longintude/latitude provided from a GPS to get the necessary information.  It is expected and strongly recommended that the `heightmap` and `texture` files are not downloaded dynamically when starting Gazebo sessions as the download process can be slow, the servers have a relatively low up-time percentage, and changing the environment is problematic for Gazebo.

> `rosrun usgs_map_retrieval get_sim_env <`*`longitude`*`> <`*`latitude`*`>`

The command creates files named `heightmap.tif`, `texture.png`, and `usgs_simulation_environment.world` which must be placed in the `package://worlds` directory.

There are various options for this command that allow one to customize it.  See:

> `rosrun usgs_map_retrieval get_sim_env -h`

All files are saved to the `worlds` directory of the `usgs_map_retrieval` package if run in ROS, or in the Current Working Directory if run without ROS.

#### Gazebo Simulation

All the files required to easily start the simulated environment in Gazebo are included in the package.  The `.world` file is automatically altered to ensure the surface of the `heightmap` intersects the origin of the Gazebo environment.  The simulation is started using the following command:

> `roslaunch usgs_map_retrieval usgs_simulation_environment.launch`

This launch file is fully compatible with the standard `empty_world.launch` file.  It can also be launched directly from `empty_world.launch` by specifying the `world_file`.  See the example:

> `roslaunch gazebo_ros empty_world.launch world_file:=usgs_simulation_environment`


## Usage without ROS

This package was developed for use with ROS and Gazebo.  It is ROS aware, but it can be used separately.  The difference is that when invoked via ROS, the `heightmap.tif`, `texture.png`, and `usgs_simulation_environment.world` files will be placed in the `worlds` subdirectory of the package automatically.  The other maps will be placed in the `config` subdirectory of the pacakge.  When used without ROS, all files will be placed in the Current Working Directory.  Gazebo, or any other environment, must be configured manually in this case.

## Citation

If this package is used for academic pursuits, please cite it as the following:

*The Greener Pastures USGS Simulation Environment Package for ROS/Gazebo*, (Version Number/Year), Lee, G., Available: https://github.com/cwru-greener-pastures/usgs_map_retrieval


(C) Copyright 2023, Gregory S. Lee, Ph.D.
