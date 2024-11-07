import arcpy
import os
from klasy import Wierzcholek, Krawedz, Graf
from func import *

#arcpy.env.workspace ="C:\studia\sem5\Pag\pag\pag.gdb"

#fc = "skjz\L4_1_BDOT10k__OT_SKJZ_L.shp"
fc="4krawedzie.shp"

graf = Graf()

with arcpy.da.SearchCursor(fc, ['OID@', 'SHAPE@', 'klasaDrogi', 'kierunek']) as cursor:
    for row in cursor:
        startPoint = row[1].firstPoint
        endPoint = row[1].lastPoint

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

        start = Wierzcholek(start_id, x1, y1)
        end = Wierzcholek(end_id, x2, y2)
        edge = Krawedz(edge_id, start, end, length, road_class, direction)
        graf.add_edge(edge)

for node in graf.nodes.values():
   print(node.id, node.edges)
   
# start_id = next(iter(graf.nodes))
# end_id = next(reversed(graf.nodes))
start_id = "471406,575311"
end_id = "471332,575482"

came_from, cost_so_far = a_star(graf, start_id, end_id,'distance')
length_a_star = cost_so_far[end_id]
path = retrieve_path2(came_from, start_id, end_id)
# print(f"Length: {length_a_star} m")
# came_from,cost_so_far = a_star(graf, start_id, end_id,'time')
# time = cost_so_far[end_id]
# print(f"Time: {time} s")

#----------wizualizacja----------------
spatial_reference = arcpy.Describe(fc).spatialReference

output_folder= "shp"
output_name = "path.shp"
arcpy.management.CreateFeatureclass(output_folder, output_name, "POLYLINE",spatial_reference=spatial_reference)
edges_list = []
for i in range(len(path)-1):
    start_node = path[i] 
    end_node = path[i + 1] 
    found_edge = False
    
    for edge in graf.edges.values():
        if (edge.from_node.id == start_node and edge.to_node.id == end_node) or (edge.from_node.id == end_node and edge.to_node.id == start_node):
            edges_list.append(edge)
            found_edge = True
            break
    if not found_edge:
        print(f"Nie znaleziono krawędzi między {start_node} i {end_node}")
        break
    
 
with arcpy.da.InsertCursor(f"{output_folder}/{output_name}", ["SHAPE@"]) as cursor:
    for edge in edges_list:
        start_point = arcpy.Point(edge.from_node.x, edge.from_node.y) 
        end_point = arcpy.Point(edge.to_node.x, edge.to_node.y)
        polyline = arcpy.Polyline(arcpy.Array([start_point, end_point])) 
        cursor.insertRow([polyline])


print("SHP done")