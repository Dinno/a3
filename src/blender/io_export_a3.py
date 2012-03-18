# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Export A3 JSON (.json)",
    "author": "Denis Kerzhemanov",
    "version": (1, 0),
    "blender": (2, 6, 0),
    "api": 36079,
    "location": "File > Export > Export A3 JSON (.json)",
    "description": "Exports set of objects to A3 WebGL engine's JSON format",
    "warning": "",
    "wiki_url": "https://github.com/Dinno/a3/wiki",
    "tracker_url": "",
    "category": "Import-Export"}

import bpy
import os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
import json

def fill_object(scene, object):
    if object.type == 'MESH':
        obj = {
            "name": None,
            "vertices": [],
            "faces": [],
            "normals": [],
            "parent": None,
            "matrix": [],
            "doubleSided": False,
            "uvs": []
#            "position": [],
#            "rotation": [],
#            "scale": []
            }
        obj["name"] = object.name
#        obj["position"] = object.location[:]
#        obj["rotation"] = object.rotation_euler[:]
#        obj["scale"] = object.scale[:]
        obj["matrix"].append(object.matrix_local[0].x)
        obj["matrix"].append(object.matrix_local[1].x)
        obj["matrix"].append(object.matrix_local[2].x)
        obj["matrix"].append(object.matrix_local[3].x)
        obj["matrix"].append(object.matrix_local[0].y)
        obj["matrix"].append(object.matrix_local[1].y)
        obj["matrix"].append(object.matrix_local[2].y)
        obj["matrix"].append(object.matrix_local[3].y)
        obj["matrix"].append(object.matrix_local[0].z)
        obj["matrix"].append(object.matrix_local[1].z)
        obj["matrix"].append(object.matrix_local[2].z)
        obj["matrix"].append(object.matrix_local[3].z)
        obj["matrix"].append(object.matrix_local[0].w)
        obj["matrix"].append(object.matrix_local[1].w)
        obj["matrix"].append(object.matrix_local[2].w)
        obj["matrix"].append(object.matrix_local[3].w)
        #print(object.matrix_local)
        #print(object.matrix_local[0].x)
        if object.parent != None:
            obj["parent"] = object.parent.name 
        m = object.to_mesh(scene, True, "RENDER")
        for v in m.vertices:
            obj["vertices"].append([v.co[0], v.co[1], v.co[2]])
        for f in m.faces:
            vertices = list(f.vertices)
            if len(vertices) == 4:
                obj["faces"].append([vertices[0], vertices[1], vertices[2], vertices[3]])
            elif len(vertices) == 3:
                obj["faces"].append([vertices[0], vertices[1], vertices[2]])
    
            #if Config.CoordinateSystem == 1:
            #    Vertices = Vertices[::-1]
            for v in [m.vertices[v] for v in vertices]:
                if f.use_smooth:
                    normal = v.normal
                else:
                    normal = f.normal
                obj["normals"].append([normal[0], normal[1], normal[2]])
        obj["doubleSided"] = m.show_double_sided

        if m.uv_textures:
            uvs = None
            for t in m.uv_textures:
                if t.active_render:
                    uvs = t.data
                    break
            
            for f in uvs:
                #verts = []
                for v in f.uv:
                    obj["uvs"].append(tuple(v))
                #if Config.CoordinateSystem == 1:
                #    Vertices = Vertices[::-1]
    #            for v in Vertices:
    #                Vertex[0], 1 - Vertex[1])
    
        return obj
    else:
        return None

def do_export(context, filepath):
    #print(context.scene)
    scene = {
        "objects": []
    }
    for o in context.scene.objects:
        jsonObj = fill_object(context.scene, o)
        if jsonObj != None:
            scene["objects"].append(jsonObj)
            
    with open(filepath, 'wb') as file:
        file.write(json.dumps(scene, indent = 4).encode(encoding='utf_8', errors='strict'))


class ExportA3JSON(bpy.types.Operator, ExportHelper):
    '''Exports set objects as a JSON object with normals and texture coordinates.'''
    bl_idname = "export_scene.a3_json"
    bl_label = "Export A3 JSON"

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
        return do_export(self, context, filepath)
        

def menu_func(self, context):
    self.layout.operator(ExportA3JSON.bl_idname, text="WebGL JSON (.json)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    #register()
    do_export(bpy.context, 'C:\\Users\\denisk\\Documents\\workspace\\a3\\test\\test.json')
