from dataclasses import dataclass, field
from typing import Any


@dataclass
class TraceEvent:
    """Un événement unique : un noeud du graphe qui s'est exécuté,
    avec ce qu'il a produit, et quand (pour calculer la latence)."""

    step_number: int
    node_name: str
    output: dict[str, Any]
    timestamp: float          # secondes écoulées depuis le début de l'exécution


@dataclass
class Trace:
    """Trace complète d'une exécution : une liste ordonnée
    d'événements,"""

    run_id: str
    events: list[TraceEvent] = field(default_factory=list)

    def node_names(self) -> list[str]:
        """Les noms des noeuds exécutés, dans l'ordre."""
        return [e.node_name for e in self.events]