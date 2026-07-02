# ruff: noqa
# mypy: ignore-errors
import numpy as np


class Tranche:
    def __init__(self, attachment: float, detachment: float, name: str = ""):
        if not (0.0 <= attachment < detachment <= 1.0):
            raise ValueError("Attachment must be < detachment and both in [0, 1]")
        self.attachment = attachment
        self.detachment = detachment
        self.name = name
        self.thickness = detachment - attachment

    def calculate_loss(self, pool_loss_fraction: np.ndarray) -> np.ndarray:
        loss = np.minimum(
            np.maximum(pool_loss_fraction - self.attachment, 0.0), self.thickness
        )
        return loss / self.thickness
