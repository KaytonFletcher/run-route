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
def generate_translation(perimeter, location):
    rand = (random.random()+1)/2
    h = rand * perimeter/4
    w = perimeter/2 - h
    lat_conversion = 68.703 + abs(location['lat']/90) * 0.704
    lng_conversion = 69.172 * math.cos(math.radians(location['lat']))
    lat = h/lat_conversion * -1 ** random.randint(0,1)
    lng = w/lng_conversion * -1 ** random.randint(0,1)
    return [lat, lng]

"""takes an origin name string and a distance length and returns a dictionary of directions of points to tuples of coordinates"""
def generate_rectangle(originAddress, distance):
    origin_dictionary = pointfinder(originAddress)
    translations = generate_translation(distance, origin_dictionary)
    origin = (origin_dictionary['lat'], origin_dictionary['lng'])
    vertical = (origin[0] + translations[0], origin[1])
    horizontal = (origin[0], origin[1] + translations[1])
    diagonal = (origin[0] + translations[0], origin[1] + translations[1])
    return {'origin': origin, 'vertical': vertical, 'diagonal': diagonal, 'horizontal': horizontal}

"""takes a dictionary from rectangle_generator, returns points formatted for nearest road API"""
def points_formatter(rectangle):
    formattedPoints = ''
    coordinates = rectangle.values()
    """return coordinates"""
    for coord in coordinates:
        formattedCoord = str(coord).replace(' ', '').replace('(','').replace(')','')
        formattedPoints += '|' + formattedCoord
    print(formattedPoints)
    return formattedPoints[1:]

"""takes a formatted string of points and returns a path through the points"""
def generate_waypoints(points):
    url = 'https://roads.googleapis.com/v1/nearestRoads?'
    resp = requests.get(url, params = {'points': points, 'key': 'AIzaSyAYO7T7rV7bUOer87rKnXLXXffZG_fh-LE'})
    results = resp.json()['snappedPoints']
    """url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?'
    results = []
    for point in points:
        resp = requests.get(url, params = {'input': point, 'inputtype': 'textquery', 'key': 'AIzaSyAYO7T7rV7bUOer87rKnXLXXffZG_fh-LE'})
        print(point)
        print(resp.json())
        results.append(resp.json()['candidates'][0]['geometry']['location'])"""
    locations = []
    for result in results:
        location = result['location']
        locations.append(location)
    points = []
    for location in locations:
        points.append((location['latitude'], location['longitude']))
    waypoints = []
    for point in points:
        if point not in waypoints:
            waypoints.append(point)
    return waypoints

def generator():
    origin = input("Origin: ")
    distance = int(input("Distance: "))
    rect = generate_rectangle(origin, distance)
    points = points_formatter(rect)
    waypoints = generate_waypoints(points)
    return waypoints
