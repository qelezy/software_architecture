from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class ProductComponent(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def get_cost(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def get_time(self) -> float:
        raise NotImplementedError

    def add(self, component: "ProductComponent", quantity: int = 1) -> None:
        raise NotImplementedError

    def remove(self, component: "ProductComponent") -> None:
        raise NotImplementedError

    def children(self) -> List[Tuple["ProductComponent", int]]:
        return []

    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        raise NotImplementedError


def component_from_dict(data: Dict[str, Any]) -> ProductComponent:
    type_name = data.get("type")
    if type_name == "composite":
        from assembly_unit import AssemblyUnit

        composite = AssemblyUnit(
            name=data["name"],
            assembly_time=float(data.get("assembly_time", 0.0)),
        )
        for child_entry in data.get("children", []):
            quantity = int(child_entry.get("quantity", 1))
            child_data = child_entry.get("component")
            if not isinstance(child_data, dict):
                continue
            child_component = component_from_dict(child_data)
            composite.add(child_component, quantity=quantity)
        return composite

    if type_name == "leaf":
        from part import Part

        return Part(
            name=data["name"],
            cost=float(data.get("cost", 0.0)),
            time=float(data.get("time", 0.0)),
        )

    raise ValueError(f"Неизвестный тип компонента: {type_name!r}")

