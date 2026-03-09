from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from product_component import ProductComponent


@dataclass
class AssemblyUnit(ProductComponent):
    assembly_time: float
    children_list: List[Tuple[ProductComponent, int]] = field(default_factory=list)

    def __init__(self, name: str, assembly_time: float) -> None:
        ProductComponent.__init__(self, name)
        self.assembly_time = float(assembly_time)
        self.children_list = []

    def add(self, component: ProductComponent, quantity: int = 1) -> None:
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным.")
        self.children_list.append((component, quantity))

    def remove(self, component: ProductComponent) -> None:
        self.children_list = [(c, q) for (c, q) in self.children_list if c is not component]

    def children(self) -> List[Tuple[ProductComponent, int]]:
        return list(self.children_list)

    def get_cost(self) -> float:
        total = 0.0
        for component, quantity in self.children_list:
            total += component.get_cost() * quantity
        return total

    def get_time(self) -> float:
        total_time = 0.0
        for component, quantity in self.children_list:
            total_time += component.get_time() * quantity
        return total_time

    def serialize(self) -> Dict[str, Any]:
        return {
            "type": "composite",
            "name": self.name,
            "assembly_time": self.assembly_time,
            "children": [
                {
                    "quantity": quantity,
                    "component": child.serialize(),
                }
                for child, quantity in self.children_list
            ],
        }

