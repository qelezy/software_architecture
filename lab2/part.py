from __future__ import annotations

from typing import Any, Dict

from product_component import ProductComponent


class Part(ProductComponent):
    def __init__(self, name: str, cost: float, time: float) -> None:
        super().__init__(name)
        self.cost = float(cost)
        self.time = float(time)

    def get_cost(self) -> float:
        return self.cost

    def get_time(self) -> float:
        return self.time

    def serialize(self) -> Dict[str, Any]:
        return {
            "type": "leaf",
            "name": self.name,
            "cost": self.cost,
            "time": self.time,
        }

