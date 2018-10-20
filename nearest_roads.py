"""https://roads.googleapis.com/v1/nearestRoads?"""
import requests
import json
import random
import math

"""takes an origin and returns its coordinates"""
def pointfinder(origin):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': origin, 'key': 'AIzaSyAYO7T7rV7bUOer87rKnXLXXffZG_fh-LE'}
    resp = requests.get(url, params=params)
    results = resp.json()['results']
    location = results[0]['geometry']['location']
    return location

"""takes a perimeter length and returns how much you need to move North, East, and Northeast for a random rectangle"""
def translation_generator(perimeter, location):
    rand = random.random()
    h = rand * perimeter/4
    w = perimeter/2 - h
    lat_conversion = 68.703 + abs(location['lat']/90) * 0.704
    lng_conversion = 69.172 * math.cos(math.radians(location['lat']))
    lat = h/lat_conversion * -1 ** random.randint(0,1)
    lng = w/lng_conversion * -1 ** random.randint(0,1)
    return [lat, lng]

"""takes an origin name string and a distance length and returns a dictionary of directions of points to tuples of coordinates"""
def rectangle_generator(originAddress, distance):
    origin_dictionary = pointfinder(originAddress)
    translations = translation_generator(distance, origin_dictionary)
    origin = (origin_dictionary['lat'], origin_dictionary['lng'])
    vertical = (origin[0] + translations[0], origin[1])
    horizontal = (origin[0], origin[1] + translations[1])
    diagonal = (origin[0] + translations[0], origin[1] + translations[1])
    return {'origin': origin, 'vertical': vertical, 'horizontal': horizontal, 'diagonal': diagonal}

"""takes a dictionary from rectangle_generator, returns points formatted for nearest road API"""
def points_formatter(rectangle):
    formattedPoints = ''
    coordinates = rectangle.values()
    for coord in coordinates:
        formattedCoord = str(coord).replace(' ', '').replace('(','').replace(')','')
        formattedPoints += '|' + formattedCoord
    return formattedPoints[1:]

"""takes a formatted string of points and returns a path through the points"""
def generate_path(points):
    url = 'https://roads.googleapis.com/v1/snapToRoads?'
    resp = requests.get(url, params = {'path': points, 'key': 'AIzaSyAYO7T7rV7bUOer87rKnXLXXffZG_fh-LE', 'interpolate': 'true'})
    results = resp.json()['snappedPoints']
    locations = []
    for result in results:
        location = result['location']
        locations.append(location)
    points = []
    for location in locations:
        points.append((location['latitude'], location['longitude']))
    print(type(location))
    print(location)
    return points
    """snappedPoints = results[0]['snappedPoints']['location']"""
    """return (location['lat'], location['lng'])"""
