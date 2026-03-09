from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from product_component import ProductComponent


@dataclass
class AssemblyUnit(ProductComponent):
    children_list: List[Tuple[ProductComponent, int]] = field(default_factory=list)

    def __init__(self, name: str) -> None:
        ProductComponent.__init__(self, name)
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "composite",
            "name": self.name,
            "children": [
                {
                    "quantity": quantity,
                    "component": child.to_dict(),
                }
                for child, quantity in self.children_list
            ],
        }

