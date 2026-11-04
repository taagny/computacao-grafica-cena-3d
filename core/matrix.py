import numpy as np


class Matrix:
    @staticmethod
    def identity() -> np.ndarray:
        return np.identity(4, dtype=np.float32)

    @staticmethod
    def translation(x: float, y: float, z: float) -> np.ndarray:
        matrix = Matrix.identity()
        matrix[0, 3] = x
        matrix[1, 3] = y
        matrix[2, 3] = z
        return matrix

    @staticmethod
    def scale(x: float, y: float, z: float) -> np.ndarray:
        return np.diag([x, y, z, 1.0]).astype(np.float32)

    @staticmethod
    def rotation_x(angle: float) -> np.ndarray:
        cosine, sine = np.cos(angle), np.sin(angle)
        return np.array(
            [
                [1, 0, 0, 0],
                [0, cosine, -sine, 0],
                [0, sine, cosine, 0],
                [0, 0, 0, 1],
            ],
            dtype=np.float32,
        )

    @staticmethod
    def rotation_y(angle: float) -> np.ndarray:
        cosine, sine = np.cos(angle), np.sin(angle)
        return np.array(
            [
                [cosine, 0, sine, 0],
                [0, 1, 0, 0],
                [-sine, 0, cosine, 0],
                [0, 0, 0, 1],
            ],
            dtype=np.float32,
        )

    @staticmethod
    def rotation_z(angle: float) -> np.ndarray:
        cosine, sine = np.cos(angle), np.sin(angle)
        return np.array(
            [
                [cosine, -sine, 0, 0],
                [sine, cosine, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ],
            dtype=np.float32,
        )

    @staticmethod
    def perspective(
        field_of_view: float,
        aspect_ratio: float,
        near: float,
        far: float,
    ) -> np.ndarray:
        focal_length = 1.0 / np.tan(field_of_view / 2.0)
        matrix = np.zeros((4, 4), dtype=np.float32)
        matrix[0, 0] = focal_length / aspect_ratio
        matrix[1, 1] = focal_length
        matrix[2, 2] = (far + near) / (near - far)
        matrix[2, 3] = (2.0 * far * near) / (near - far)
        matrix[3, 2] = -1.0
        return matrix

    @staticmethod
    def look_at(
        eye: np.ndarray,
        target: np.ndarray,
        up: np.ndarray,
    ) -> np.ndarray:
        forward = target - eye
        forward = forward / np.linalg.norm(forward)
        side = np.cross(forward, up)
        side = side / np.linalg.norm(side)
        corrected_up = np.cross(side, forward)

        matrix = Matrix.identity()
        matrix[0, :3] = side
        matrix[1, :3] = corrected_up
        matrix[2, :3] = -forward
        matrix[0, 3] = -np.dot(side, eye)
        matrix[1, 3] = -np.dot(corrected_up, eye)
        matrix[2, 3] = np.dot(forward, eye)
        return matrix
