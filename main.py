import random
import urllib.request
from pathlib import Path
import math
import browser_cookie3

TILE_SIZE = 512
ZOOM_MIN = 10
ZOOM_MAX = 15


def get_auth_strava_url():
    """Get URL from strava.com/heatmap with auth data"""
    # Get cookiejar object from Chrome and serialize into dict
    cj = browser_cookie3.chrome(domain_name='.strava.com').__dict__
    # Get the required values as strings
    try:
        cloud_front_key_pair_id = cj['_cookies']['.strava.com']['/']['CloudFront-Key-Pair-Id'].value
        cloud_front_policy = cj['_cookies']['.strava.com']['/']['CloudFront-Policy'].value
        cloud_front_signature = cj['_cookies']['.strava.com']['/']['CloudFront-Signature'].value
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments: {1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        print('Please login to https://strava.com/heatmap')
        raise

    # Build the URL with auth data
    auth_strava_url = 'https://heatmap-external-{0}.strava.com/tiles-auth/ride/hot/{1}/{2}/{' \
                      '3}.png?Key-Pair-Id=CloudFront-Key-Pair-Id&Policy=CloudFront-Policy&Signature=' \
                      'CloudFront-Signature'
    auth_strava_url = auth_strava_url.replace('CloudFront-Key-Pair-Id', str(cloud_front_key_pair_id))
    auth_strava_url = auth_strava_url.replace('CloudFront-Policy', str(cloud_front_policy))
    auth_strava_url = auth_strava_url.replace('CloudFront-Signature', str(cloud_front_signature))
    return auth_strava_url


def get_tile_coordinates(lat_long, zoom_level):
    """Calculation of tile coordinates from google maps coordinates"""
    scale = 1 << zoom_level
    # World coordinates
    siny = math.sin((lat_long[0] * math.pi) / 180)
    # Truncate to +-0.9999
    siny = min(max(siny, -0.9999), 0.9999)
    xy_world = [TILE_SIZE * (0.5 + lat_long[1] / 360),
                TILE_SIZE * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi))]
    # Tiles coordinates
    return [math.floor((xy_world[0] * scale) / TILE_SIZE), math.floor((xy_world[1] * scale) / TILE_SIZE)]


err_counter = 0
download_counter = 0
print('Login to https://strava.com/heatmap in Chrome browser and specify coordinates in WGS84 standard \n'
      'aka Google Maps coordinates, top-left and-bottom right points of the desired region. ')
coordinates_lat_long_1 = input('Enter starting coordinates, Lat,Long ')
coordinates_lat_long_2 = input('Enter end coordinates, Lat,Long ')

lat_long_1 = list(map(float, coordinates_lat_long_1.split(',')))
lat_long_2 = list(map(float, coordinates_lat_long_2.split(',')))

# Recount upper left and bottom right points of the map coordinates
sort_lat = sorted([lat_long_1[0], lat_long_2[0]], reverse=True)
sort_long = sorted([lat_long_1[1], lat_long_2[1]])
lat_long_1[0] = sort_lat[0]
lat_long_1[1] = sort_long[0]
lat_long_2[0] = sort_lat[1]
lat_long_2[1] = sort_long[1]
print('Lat1 = ', lat_long_1[0], 'Long1 = ', lat_long_1[1])
print('Lat2 = ', lat_long_2[0], 'Long2 = ', lat_long_2[1], end='\n\n')

# Debug purposes
for z in range(ZOOM_MIN, ZOOM_MAX + 1):
    xy_tiles1 = get_tile_coordinates(lat_long_1, z)
    xy_tiles2 = get_tile_coordinates(lat_long_2, z)
    print('Tiles coordinates1 = ', xy_tiles1)
    print('Tiles coordinates2 = ', xy_tiles2)
    print('Zoom level         = ', z, end='\n\n')

# Make download folder
path = Path.cwd()
print("The current working directory is %s" % path)
path = Path(path, 'Strava_tiles')
Path(path).mkdir(parents=True, exist_ok=True)

# Make the .metainfo file
Path(path, '.metainfo').write_text('[url_template]\nhttp://localhost\n[randoms]\n\n[min_zoom]\n0\n[max_zoom]\n'
                                   '15\n[ellipsoid]\nfalse\n[inverted_y]\nfalse\n[tile_size]\n512\n[img_density]\n'
                                   '16\n[avg_img_size]\n32000\n[ext]\n.png\n[expiration_time_minutes]\n0\n')

url = get_auth_strava_url()

# make Zoom dir
for z in range(ZOOM_MIN, ZOOM_MAX + 1):
    xy_tiles1 = get_tile_coordinates(lat_long_1, z)
    xy_tiles2 = get_tile_coordinates(lat_long_2, z)
    path_z = Path(path, str(z))
    Path(path_z).mkdir(parents=True, exist_ok=True)
    # Make X coordinate dir
    for x in range(xy_tiles1[0], xy_tiles2[0] + 1):
        path_z_x = Path(path_z, str(x))
        Path(path_z_x).mkdir(parents=True, exist_ok=True)
        # Download Y coordinate named files
        for y in range(xy_tiles1[1], xy_tiles2[1] + 1):
            url_f = url.format(random.choice(['a', 'b', 'c']), str(z), str(x), str(y))
            filename = Path(path_z_x, str(y) + '.png.tile')
            if Path(filename).is_file():
                print(filename, ' Already exist')
            else:
                try:
                    urllib.request.urlretrieve(url_f, Path(path_z_x, str(y) + '.png.tile'))
                    print(filename, ' Downloaded.')
                    download_counter += 1
                except Exception as e:
                    print(' \nERROR!!! URL EXCEPTION! ', str(e), '\n', url_f, end='\n\n')
                    err_counter += 1
                    pass

print('Download finished. \n Downloaded ', download_counter, ' files\n Errors ', err_counter)
