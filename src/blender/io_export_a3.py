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
from mathutils import *


def get_material_texture(material):
    if material:
        #Create a list of Textures that have type "IMAGE"
        imageTextures = [material.texture_slots[textureSlot].texture for textureSlot in material.texture_slots.keys() 
                         if material.texture_slots[textureSlot].use and material.texture_slots[textureSlot].texture.type == "IMAGE"]
        #Refine a new list with only image textures that have a file source
        imageFiles = [bpy.path.basename(texture.image.filepath) for texture in imageTextures if getattr(texture.image, "source", "") == "FILE"]
        if imageFiles:
            return imageFiles[0]
    return None

def export_material(material):
    return {
        "diffuseColor": list(material.diffuse_color),
        "diffuseIntensity": material.diffuse_intensity,
        "specularColor": list(material.specular_color),
        "specularIntensity": material.specular_intensity,
        "specularShininess": material.specular_hardness,
        "texture": get_material_texture(material) 
    } 

def export_materials(mesh):
    if len(mesh.materials) == 0:
        return None
    else:
        return export_material(mesh.materials[0]) 

def export_matrix(matrix):
    exportedMatrix = []
    exportedMatrix.append(matrix[0].x)
    exportedMatrix.append(matrix[1].x)
    exportedMatrix.append(matrix[2].x)
    exportedMatrix.append(matrix[3].x)
    exportedMatrix.append(matrix[0].y)
    exportedMatrix.append(matrix[1].y)
    exportedMatrix.append(matrix[2].y)
    exportedMatrix.append(matrix[3].y)
    exportedMatrix.append(matrix[0].z)
    exportedMatrix.append(matrix[1].z)
    exportedMatrix.append(matrix[2].z)
    exportedMatrix.append(matrix[3].z)
    exportedMatrix.append(matrix[0].w)
    exportedMatrix.append(matrix[1].w)
    exportedMatrix.append(matrix[2].w)
    exportedMatrix.append(matrix[3].w)
    return exportedMatrix

def export_faces(mesh):
    faces = []
    for f in mesh.faces:
        vertices = f.vertices
        if len(vertices) == 4:
            faces.append([vertices[0], vertices[1], vertices[2], vertices[3]])
        elif len(vertices) == 3:
            faces.append([vertices[0], vertices[1], vertices[2]])
    return faces
    
def export_normals(mesh):
    normals = []
    for f in mesh.faces:
        #if Config.CoordinateSystem == 1:
        #    Vertices = Vertices[::-1]
        for v in [mesh.vertices[v] for v in f.vertices]:
            if f.use_smooth:
                normal = v.normal
            else:
                normal = f.normal
            normals.append([normal[0], normal[1], normal[2]])
    return normals

def export_object(scene, object):
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
        obj["matrix"] = export_matrix(object.matrix_local)
        if object.parent != None:
            obj["parent"] = object.parent.name 
        m = object.to_mesh(scene, True, "RENDER")
        for v in m.vertices:
            obj["vertices"].append([v.co[0], v.co[1], v.co[2]])
        obj["faces"] = export_faces(m)
        obj["normals"] = export_normals(m)
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
        obj["material"] = export_materials(m)
        
        return obj
    else:
        return None

def do_export(context, filepath):
    #print(context.scene)
    scene = {
        "objects": []
    }
    for o in context.scene.objects:
        jsonObj = export_object(context.scene, o)
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
    #do_export(bpy.context, 'C:\\Users\\denisk\\Documents\\workspace\\a3\\test\\test.json')
    do_export(bpy.context, os.path.basename(os.path.splitext(bpy.data.filepath)[0]) + '.json')
