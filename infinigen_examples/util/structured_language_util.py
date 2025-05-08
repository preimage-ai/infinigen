from infinigen.core.constraints.example_solver import state_def
from infinigen.core.constraints.constraint_language.constants import RoomConstants
from infinigen.core.constraints.constraint_language.relations import ConnectorType
from infinigen.core import tags
from shapely import Polygon
from shapely import ops
import open3d as o3d
import numpy as np

class StructuredLanguageWriter:
    def __init__(self, constants: RoomConstants):
        self.constants = constants

    def write(self, state: state_def.State):
        # Convert the state to a structured language representation
        # This is a placeholder implementation. You should replace this with actual logic.
        meshes = []
        polygon_dict = {}
        for obj_name, object in state.objs.items():
            if tags.Semantics.Room in object.tags:
                # Create open3d mesh from shapely.polygon
                polygon = object.polygon
                polygon_dict[obj_name] = polygon
        
        for obj_name, object in state.objs.items():
            if tags.Semantics.Room in object.tags:
                for relation in object.relations:        
                    if ConnectorType.Open in relation.relation.connector_types and obj_name in polygon_dict:
                        polygon1 = object.polygon
                        polygon2 = state.objs[relation.target_name].polygon
                        if polygon1.intersects(polygon2):
                            combined_polygon = ops.unary_union([polygon1, polygon2])
                        polygon_dict[obj_name] = combined_polygon
                        del polygon_dict[relation.target_name]
                        # breakpoint()
        
        for obj_name, polygon in polygon_dict.items():
            # Extrude the shapely polygon to create a 3D mesh
            height = self.constants.wall_height
            wall_thickness = self.constants.wall_thickness
            vertices = []
            faces = []

            # Adjust for wall thickness by offsetting the polygon
            offset_polygon = polygon.buffer(-wall_thickness / 2, join_style=2)
            offset_coords = list(offset_polygon.exterior.coords)
            num_vertices = len(offset_coords)

            for x, y in offset_coords:
                vertices.append([x, y, wall_thickness / 2])  # Bottom vertices (offset)
                vertices.append([x, y, height- wall_thickness / 2])  # Top vertices (offset)
                # print ("({:.2f} {:.2f}), ".format(x, y), end="")
            # print ()
            # Create faces for the sides
            for i in range(num_vertices):
                next_i = (i + 1) % num_vertices
                faces.append([i * 2, next_i * 2, i * 2 + 1])  # Side triangle 1
                faces.append([i * 2 + 1, next_i * 2, next_i * 2 + 1])  # Side triangle 2

            # Create faces for the top and bottom
            # bottom_face = [i * 2 for i in range(num_vertices)]
            # top_face = [i * 2 + 1 for i in range(num_vertices)]
            # faces.extend([bottom_face, top_face])

            # Create the open3d mesh
            mesh = o3d.geometry.TriangleMesh()
            mesh.vertices = o3d.utility.Vector3dVector(vertices)
            mesh.triangles = o3d.utility.Vector3iVector(faces)
            mesh.compute_vertex_normals()
            mesh.paint_uniform_color(np.random.rand(3))  # Random color for visualization
            meshes.append(mesh)
        
        mesh_final = sum(meshes, start=o3d.geometry.TriangleMesh())  # Combine all meshes into one
        # o3d.visualization.draw(mesh_final)
        o3d.io.write_triangle_mesh("output_mesh.ply", mesh_final)  # Save the mesh to a file
    def save_mesh(self):
        pass