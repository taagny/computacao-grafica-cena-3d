import numpy as np

from core.attribute import Attribute
from core.base import Base
from core.matrix import Matrix
from core.texture import Texture
from materials.base import Material
from materials.lambert import LambertMaterial


class Object3D(Base):
    def __init__(
        self,
        attributes: dict[str, Attribute] | None = None,
        color: tuple[float, float, float] = (1.0, 1.0, 1.0),
        texture: Texture | None = None,
        material: Material | None = None,
    ) -> None:
        self.position = np.zeros(3, dtype=np.float32)
        self.rotation = np.zeros(3, dtype=np.float32)
        self.scale = np.ones(3, dtype=np.float32)
        self.color = color
        self.texture = texture
        self.material = material if material is not None else LambertMaterial()
        self.attributes = attributes or {}
        self.children: list[Object3D] = []
        self.parent: Object3D | None = None

    def add(self, child: "Object3D") -> None:
        if child is self or self._is_descendant_of(child):
            raise ValueError("A hierarquia de objetos nao pode conter ciclos.")
        if child.parent is not None:
            child.parent.remove(child)
        child.parent = self
        self.children.append(child)

    def remove(self, child: "Object3D") -> None:
        self.children.remove(child)
        child.parent = None

    def _is_descendant_of(self, possible_ancestor: "Object3D") -> bool:
        current = self.parent
        while current is not None:
            if current is possible_ancestor:
                return True
            current = current.parent
        return False

    def local_matrix(self) -> np.ndarray:
        translation = Matrix.translation(*self.position)
        rotation = (
            Matrix.rotation_z(float(self.rotation[2]))
            @ Matrix.rotation_y(float(self.rotation[1]))
            @ Matrix.rotation_x(float(self.rotation[0]))
        )
        scaling = Matrix.scale(*self.scale)
        return translation @ rotation @ scaling

    def iter_objects(
        self,
        parent_matrix: np.ndarray | None = None,
    ):
        world_matrix = self.local_matrix()
        if parent_matrix is not None:
            world_matrix = parent_matrix @ world_matrix
        yield self, world_matrix
        for child in self.children:
            yield from child.iter_objects(world_matrix)

    def update(self, delta_time: float) -> None:
        for child in self.children:
            child.update(delta_time)

    def dispose(self) -> None:
        for child in self.children:
            child.dispose()
        for attribute in self.attributes.values():
            attribute.dispose()
        if self.texture is not None:
            self.texture.dispose()
            self.texture = None
        self.children.clear()
        self.attributes.clear()
