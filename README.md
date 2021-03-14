# **Strava_Heatmap_Download**

Download Strava Heatmap tiles for OsmAnd app.

Login to https://strava.com/heatmap in Chrome browser. Run script and specify coordinates
in WGS84 standard aka Google Maps coordinates, top-left and-bottom right points of the desired region.

For example:
Enter starting coordinates, Lat,Long 50.994544, 4.594678
Enter end coordinates, Lat,Long 50.969628, 4.645655

A 'Strava_tiles' folder will be created, containing the .metainfo file and folders 
with downloaded tiles in .png format ('10974.png.tile' for example).
Copy the 'Strava_tiles' folder to /storage/emulated/0/Android/data/net.osmand.plus/files/tiles
of your Android device. 
In Osmand select the overlay map as 'Strava_tiles'.
