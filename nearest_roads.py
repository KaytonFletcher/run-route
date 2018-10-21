"""https://roads.googleapis.com/v1/nearestRoads?"""
import requests
import json
import random
import math
import re

class PathFinder:
    origin = None
    distance = 0
    rect = None
    points = None
    directions = []
    key = 'AIzaSyAYO7T7rV7bUOer87rKnXLXXffZG_fh-LE'

    """takes an origin and returns its coordinates"""
    def pointfinder(self):
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'address': self.origin, 'key': 'AIzaSyAYO7T7rV7bUOer87rKnXLXXffZG_fh-LE'}
        resp = requests.get(url, params=params)
        results = resp.json()['results']
        location = results[0]['geometry']['location']
        return location

    """takes a perimeter length and returns how much you need to move North, East, and Northeast for a random rectangle"""
    def translation_generator(self, perimeter, location):
        rand = (random.random()+1)/2
        h = rand * perimeter/4
        w = perimeter/2 - h
        lat_conversion = 68.703 + abs(location['lat']/90) * 0.704
        lng_conversion = 69.172 * math.cos(math.radians(location['lat']))
        lat = h/lat_conversion * -1 ** random.randint(0,1)
        lng = w/lng_conversion * -1 ** random.randint(0,1)
        return [lat, lng]

    """takes an origin name string and a distance length and returns a dictionary of directions of points to tuples of coordinates"""
    def generate_rectangle(self):
        origin_dictionary = self.pointfinder()
        translations = self.translation_generator(self.distance, origin_dictionary)
        origin = (origin_dictionary['lat'], origin_dictionary['lng'])
        vertical = (origin[0] + translations[0], origin[1])
        horizontal = (origin[0], origin[1] + translations[1])
        diagonal = (origin[0] + translations[0], origin[1] + translations[1])
        return {'origin': origin, 'vertical': vertical, 'diagonal': diagonal, 'horizontal': horizontal}

    """takes a dictionary from rectangle_generator, returns points formatted for nearest road API"""
    def points_formatter(self):
        formattedPoints = ''
        coordinates = self.rect.values()
        for coord in coordinates:
            formattedCoord = str(coord).replace(' ', '').replace('(','').replace(')','')
            formattedPoints += '|' + formattedCoord
        print(formattedPoints[1:])
        return formattedPoints[1:]

    """takes a formatted string of points and returns a path through the points"""
    def generate_path(self):
        self.points = self.points.split("|")
        for i in range(0,4):
            if abs(float(self.points[i].split(',')[1])-float(self.points[i+1 if i !=3 else 0].split(',')[1]))>abs(float(self.points[i].split(',')[0])-float(self.points[i+1 if i !=3 else 0].split(',')[0])):
                if float(self.points[i].split(',')[1])>float(self.points[i+1 if i !=3 else 0].split(',')[1]):
                    self.directions.append('west')
                else:
                    self.directions.append('east')
            else:
                if float(self.points[0].split(',')[0])>float(self.points[i+1].split(',')[0]):
                    self.directions.append('south')
                else:
                    self.directions.append('north')
        dir_url = 'https://maps.googleapis.com/maps/api/directions/json?'
        # distance = 0
        waypoints = []
        i = 0
        max_distance = self.distance / 4
        while i<4:
            dir_resp = requests.get(dir_url, params={'origin':self.points[i], 'destination':self.points[i+1 if i<3 else 0],'mode': 'walking', 'key': self.key},)
            dir_results = json.loads(dir_resp.content)
            if len(dir_results["routes"]) != 0:
                distance = float(dir_results['routes'][0]['legs'][0]['distance']['text'].replace(' mi',''))
            else:
                return False
            if distance > max_distance or distance == 0:
                if(self.directions[i] == 'north'):
                    val = str(float(self.points[i+1 if i<3 else 0].split(',')[0]) - .006) + ','
                    self.points[i+1 if i<3 else 0] = self.points[i+1 if i<3 else 0].split(',')[1]
                    self.points[i+1 if i<3 else 0] = val + self.points[i+1 if i<3 else 0]
                elif(self.directions[i] == 'south'):
                    val = str(float(self.points[i + 1 if i < 3 else 0].split(',')[0]) + .006) + ','
                    self.points[i + 1 if i < 3 else 0] = self.points[i+1 if i<3 else 0].split(',')[1]
                    self.points[i+1 if i<3 else 0] = val + self.points[i+1 if i<3 else 0]
                elif (self.directions[i] == 'east'):
                    val = ',' + str(float(self.points[i + 1 if i < 3 else 0].split(',')[1]) - .006)
                    self.points[i + 1 if i < 3 else 0] = self.points[i+1 if i<3 else 0].split(',')[0]
                    self.points[i+1 if i<3 else 0] = self.points[i+1 if i<3 else 0] +val
                elif (self.directions[i] == 'west'):
                    val = ',' + str(float(self.points[i + 1 if i < 3 else 0].split(',')[1]) + .006)
                    self.points[i + 1 if i < 3 else 0] = self.points[i+1 if i<3 else 0].split(',')[0]
                    self.points[i+1 if i<3 else 0] = self.points[i+1 if i<3 else 0] + val
            else:
                max_distance = max_distance + (max_distance - distance)*.5
                print("Found best path for {}".format(self.directions[i]))
                i = i+1
            print(distance)

        # roads_url = 'https://roads.googleapis.com/v1/nearestRoads?'
        # roads_resp = requests.get(roads_url, params={'points': self.points, 'key': self.key})
        # try:
        #     roads_results = roads_resp.json()['snappedPoints']
        #     locations = []
        #     for result in roads_results:
        #         location = result['location']
        #         locations.append(location)
        #     points = []
        #     for location in locations:
        #         points.append((location['latitude'], location['longitude']))
        #     for point in points:
        #         if point not in waypoints:
        #             waypoints.append(point)
        # except:
        #     return False
        # self.points = waypoints
        return True

def full():
    pathfinder = PathFinder()
    pathfinder.origin = input("Origin: ")
    pathfinder.distance = int(input("Distance: "))
    pathfinder.distance = pathfinder.distance - pathfinder.distance*.3
    pathfinder.rect = pathfinder.generate_rectangle()
    pathfinder.points = pathfinder.points_formatter()
    if(pathfinder.generate_path()):
        print(json.dumps(pathfinder.points))
    print("https://www.google.com/maps/dir/?api=1&origin={}&waypoints={}&destination={}&travelmode=walking".format(pathfinder.points[0],pathfinder.points_formatter(),pathfinder.points[0]))

    return pathfinder.points
full()

