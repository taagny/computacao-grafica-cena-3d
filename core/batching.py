"""Bake static parts by material, retaining every articulated pivot.

Models are authored with primitives, then their fixed parts are concatenated
into GPU meshes. Local vertex positions and inverse-transpose normals are
baked once, so hundreds of primitives need far fewer draw calls each frame.
"""
from collections import defaultdict
import numpy as np
from geometries.base import Geometry


def batch_static(root, animated=()):
    animated = set(animated)
    groups = defaultdict(list)
    removed = []

    def collect(obj, parent_matrix):
        if obj in animated:
            batch_static(obj,animated)
            return
        matrix = parent_matrix @ obj.local_matrix()
        if "a_position" in obj.attributes:
            key = (tuple(obj.color),id(obj.texture),obj.material.model,
                   tuple(obj.material.specular_color),obj.material.shininess,
                   obj.emission,obj.cast_shadow,getattr(obj,"scan_surface",False))
            groups[key].append((obj,matrix))
        for child in obj.children:
            collect(child,matrix)

    identity = np.eye(4,dtype=np.float32)
    for child in list(root.children):
        collect(child,identity)
        if child not in animated:
            removed.append(child)
    for key,entries in groups.items():
        positions,normals,uvs = [],[],[]
        for obj,matrix in entries:
            points = obj.attributes["a_position"].data
            positions.append(points @ matrix[:3,:3].T + matrix[:3,3])
            normal = obj.attributes["a_normal"].data @ np.linalg.inv(matrix[:3,:3])
            normal /= np.linalg.norm(normal,axis=1,keepdims=True)
            normals.append(normal)
            uvs.append(obj.attributes["a_uv"].data if "a_uv" in obj.attributes else np.zeros((len(points),2)))
        first = entries[0][0]
        mesh = Geometry(np.concatenate(positions),first.color,np.concatenate(uvs),
                        texture=first.texture,normals=np.concatenate(normals),material=first.material)
        mesh.emission,mesh.cast_shadow,mesh.scan_surface = key[-3:]
        root.add(mesh)
    # Texture ownership moved to the batched meshes; don't delete it here.
    for entries in groups.values():
        for obj,_ in entries:
            obj.texture = None
    for child in removed:
        root.remove(child)
        child.dispose()
