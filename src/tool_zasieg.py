import arcpy
import os
from klasy import Wierzcholek, Krawedz, Graf
from func import create_reachability_map, add_shp_to_map, create_reachability_shp
arcpy.env.overwriteOutput = True

'''
Parametry do toola:
0. fc Feature Layer - warstwa z siecią dróg
1. warstwa_punktowa_zasieg Feature Set - warstwa punktowa z jednym obiektem
2. travel_time Double - czas w minutach
'''

fc = arcpy.GetParameterAsText(0)
spatial_reference = arcpy.Describe(fc).spatialReference
warstwa_punktowa_zasieg = arcpy.GetParameterAsText(1)
travel_time = int(arcpy.GetParameterAsText(2)) * 60 # [s]

output_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shp")
os.makedirs(output_folder, exist_ok=True)

graf = Graf()
with arcpy.da.SearchCursor(fc, ['OID@', 'SHAPE@', 'klasaDrogi', 'kierunek']) as cursor:
    for row in cursor:
        startPoint = row[1].firstPoint
        endPoint = row[1].lastPoint
        geometry = row[1].WKT

        x1 = startPoint.X
        y1 = startPoint.Y

        x2 = endPoint.X
        y2 = endPoint.Y

        edge_id = row[0]
        length = int(row[1].length)
        road_class = row[2]
        direction = row[3]

        start_id = str(int(x1)) + "," + str(int(y1))
        end_id = str(int(x2)) + "," + str(int(y2))

        start = graf.add_node(Wierzcholek(start_id, x1, y1))
        end = graf.add_node(Wierzcholek(end_id, x2, y2))

        edge = Krawedz(edge_id, start, end, length, road_class, direction, geometry)
        graf.add_edge(edge)
        
    
points_zasieg = []
with arcpy.da.SearchCursor(warstwa_punktowa_zasieg, ['SHAPE@X','SHAPE@Y']) as cursor:
    for row in cursor:
        x, y = row[0], row[1]
        points_zasieg.append((x,y))
        arcpy.AddMessage(points_zasieg)

if len(points_zasieg) == 1:
    x, y = points_zasieg[0]

    point_zasieg = graf.snap(x, y)
    arcpy.AddMessage(f"Point: {point_zasieg}")

else:
    arcpy.AddMessage("W warstwie punktowej do wyznaczenia zasięgu powinien znajdować się 1 punkt!")
    exit()

output_name_zasieg = "zasieg.shp"
output_path_zasieg = os.path.join(output_folder, output_name_zasieg)

arcpy.management.CreateFeatureclass(output_folder, output_name_zasieg, "POLYLINE", spatial_reference=spatial_reference)
arcpy.AddField_management(f"{output_folder}/{output_name_zasieg}", "TravelTime", "FLOAT")
reachable_nodes, came_from = create_reachability_map(graf, point_zasieg.id, travel_time)
create_reachability_shp(graf, output_path_zasieg, reachable_nodes, came_from)
add_shp_to_map(output_path_zasieg)
