from django.shortcuts import render
import os
import json
import sys
from geopy import Nominatim
import haversine as hs
from django.conf import settings
from django.http import HttpResponseRedirect
from .forms import Input, SubForm
from django.http import HttpResponse
from shapely.geometry import LineString

# Create your views here.
sys.setrecursionlimit(1000000)
def create_graph():
    file1 = open('parsed_data.json', 'r')
    data = file1.read()
    obj = json.loads(data)
    list1 = obj['features']

    graph2 = {}
    for i in list1:
        from_node = i["properties"]["From Node0"]
        to_node = i["properties"]["To Node0"]
        distance = i["properties"]["Length0"]
        temp = {to_node: distance}
        if from_node not in graph2.keys():
            graph2[from_node] = temp
        elif from_node in graph2.keys():
            graph2[from_node].update(temp)
    return graph2

def get_list():
    file1 = open('parsed_data.json', 'r')
    data = file1.read()
    obj = json.loads(data)
    list1 = obj['features']
    return list1

#get_input() function is responsible for handling the request received from the form and acts as a
def get_input(request):
    print(request.POST)
    if request.method == 'POST':
        loc = Nominatim(user_agent="GetLoc")
        start_loc = loc.geocode(request.POST['start'])
        fin_start_loc = [start_loc.longitude, start_loc.latitude]
        end_loc = loc.geocode(request.POST['end'])
        fin_end_loc = [end_loc.longitude, end_loc.latitude]
        start = closest(construct_tree(pop_parsed_data()), fin_start_loc)
        end = closest(construct_tree(pop_parsed_data()), fin_end_loc)
        for i in get_list():
            if i["geometry"]["coordinates"][0] == start:
                start = i["properties"]["From Node0"]
            elif i["geometry"]["coordinates"][0] == end:
                end = i["properties"]["To Node0"]
        intstart = int(start)
        intend = int(end)
        route = dijkstra(intstart, intend)
        coord_list = construct_results(route)
    return render(request, 'main.html', {'coord_list':coord_list})


def home(request):
    return render(request, 'main.html')


# def SubForm_process(request):
#     if request.method == 'POST':
#         form = SubForm(request.POST)
#         if form.is_valid():
#             form.save()
#     form = SubForm()
#     return render(request, 'main.html', {'form': form})

#construct_results() function is responsible for fromatting the data in a way, that can
# be passed to the 'main.html' template to use it on the map highlighting the route.
def construct_results(data):
    coord_list = []
    with open("print_results.json", "w") as outfile:
        for i in range(len(data)):
            current_item = data[i]
            if i < len(data)-1:
                next_item = data[i+1]
                for j in get_list():
                    if j["properties"]["From Node0"] == current_item and j["properties"]["To Node0"] == next_item:
                        line = json.dumps(j, indent=4)
                        outfile.write(line)
                        for k in j["geometry"]["coordinates"]:
                            coord_list.append(k)
    return coord_list


# Graph is created and populated from the data held in parsed_data.json

def dijkstra(start, end):
    """_summary_

    Args:
        graph2 (Dictionary): A dictionary of dictionaries which hold the
        neighbours and their respective distances.
        start (node_id):starting point(port)
        end (node_id): destination(port)
    """
    graph2 = create_graph()
    shortest_dist = {}
    prev_nodes = {}
    unvisited = graph2
    route = []

    #Initialises the infinite distance for all port nodes, except from the start
    #which is set to 0 since it is the starting point.
    for n in unvisited:
        shortest_dist[n] = 999999
    shortest_dist[start] = 0

    # print(shortest_dist[end])
    #The loop runs until all nodes are visited
    while unvisited:
        closest = None
        for n in unvisited:
            if closest is None:
                closest = n
            if shortest_dist[n] < shortest_dist[closest]:
                closest = n

        possible_next_n = graph2[closest].items()
        print(possible_next_n)

        #the distance of the neghbouring nodes, is checked, to find the one with the smallest
        #value and add it to the prev_nodes dictionary keeping track of the closest neighbours.

        for key, val in possible_next_n:
            #check if there is a KeyError.
            try:
                if shortest_dist[key] > val + shortest_dist[closest]:
                    shortest_dist[key] = val + shortest_dist[closest]
                    prev_nodes[key] = closest
                    print("NODE ADDITION SUCCESSFUL", prev_nodes[key])
            except KeyError:
                print("NODE ADDITION FAILED")
                break
        #after the neighbours have been visited and the distances determined, the current node is
        #removed from the unvisited list using the pop() function.
        unvisited.pop(closest)
    destination = end

    #Building the final route list backwards by accessing the prev_nodes dictionary and adding it to
    #the route list which is finally returned in the end of the function.
    while destination != start:
        #Check for KeyError
        try:
            #Add destination value to the first position of the route list
            route.insert(0, destination)
            destination = prev_nodes[destination]
            #Checks that the addition of the node to the route list is successful
            print("OK", destination)
        except KeyError:
            #Error message printed in the console if there is a KeyError and the node
            #could not be added.
            print("NOT OK", destination)
            break
    print (possible_next_n)
    #The start node is added last in the first position in the list
    route.insert(0, start)
    return route
    #FOR TESTING:
    # print("The desired route from point A to point B is: ", route)
    # print("The number of stop suggested: ", len(route) - 2)

def pop_parsed_data():
    parsed_data_list = []
    for i in get_list():
        parsed_data_list.append(i["geometry"]["coordinates"][0])
    return parsed_data_list


# print (user_input)
# print("The length of the list is", len(pop_parsed_data()))

# get input from user for two points. TESTING ONLY
def start_list():
    start_list = []
    for i in range(0, 2):
        start_node = float(input("Enter starting coordinates: "))
        start_list.append(start_node)
    # start_list.reverse()
    return start_list

# print("The coordinates from the given address are:", start_list)


# testing function to check if the results obtained by the closest()
# are correct. -----------------TEST ONLY----------------------
# def actual_closest_point_in_list():
#     list1 = create_graph()
#     closest_p = list1[0]["geometry"]["coordinates"][0]
#     for i in list1:
#         current_point = i["geometry"]["coordinates"][0]
#         if hs.haversine(start_list, current_point) < hs.haversine(start_list, closest_p):
#             closest_p = current_point
#     return closest_p


# search the parsed_data.json to check if the address exists,
# if not call find_nearest_coord() to get the closest one in
# the data set.
#----------------TEST ONLY--------------------------
# def search_data():
#     for i in list1:
#         if start_list == i["geometry"]["coordinates"][0] :
#             print ("OK")
#         else:
#             print("NOT OK")

dim = 2
#Recursive function to construct the tree used in the main search function.
#The principle is that the data are divided in half as many times as possibles.
# Moreover, it creates the branches of the tree
def construct_tree(nodes, height=0):
    nl = len(nodes)

    if nl <= 0:
        return None
    split_point = height % dim
    sorted_node_list = sorted(nodes, key=lambda i: i[split_point])
    results = {
        'node': sorted_node_list[round(nl / 2)],
        'right': construct_tree(sorted_node_list[round(nl / 2 + 1):], height + 1),
        'left': construct_tree(sorted_node_list[:round(nl / 2)], height + 1)
    }
    return results


#compare() function takes three argument of node type. The distance between the switch_node
# and the other two is calculated respectively and the shortest one is returned.
#This acts as a helper function for the closest().
def compare(switch_node, node2, node3):
    if node2 is None:
        return node3
    if node3 is None:
        return node2

    lat1, lon1= switch_node
    lat2, lon2 = node2
    lat3, lon3 = node3

    node2_dist = (lat1-lat2)**2 + (lon1-lon2)**2
    node3_dist = (lat1-lat3)**2 + (lon1-lon3)**2
    #dist(switch_node, node3)

    if node2_dist > node3_dist:
        return node3
    else:
        return node2

#The following function is the one performing the actual search. Initially, it determines the branch of the
#tree that the desired point likely exists and visits that, reducing the number of items it has to go through.
#Takes three arguments: the "current" parameter is the list of points-nodes that will be searched
#The "node" argument is the input from the user and is the node that we use as a reference to find the closest one in the list.
#the height  counts the "distance" from the root node.
def closest(tree, node, height=0):
    split_point = height % dim
    if tree is None:
        return None

    print(type(node[split_point]))
    print(type(tree['node'][split_point]))
    start_pos = tree['node'][split_point]

    #The following if/else statement, determines the branch that the algorithm will follow.
    if node[split_point] > start_pos:
        next = tree['right']
        opp = tree['left']
    else:
        next = tree['left']
        opp = tree['right']

    #final is a node is equal to what the compare function return which is the closest
    #node to the "node" parameter.
    final = compare(node, closest(next, node, height + 1), tree['node'])
    #Calculate the distance between the node and the final (node) .
    lat, lon = node
    lat2, lon2 = final
    total_dist = (lat - lat2) ** 2 + (lon - lon2) ** 2

    #Check if there is a point closer compared to the one previously calculated.
    if total_dist > (node[split_point] - start_pos) ** 2:
        final = compare(node, closest(opp, node, height + 1), final)

    print("THE NODE FOUND TO BE THE CLOSEST TO THE POINT GIVEN BY THE USER IS: ", final)
    return final

# closest_point = closest(construct_tree(pop_parsed_data()), start_list)
# print(closest_point)

