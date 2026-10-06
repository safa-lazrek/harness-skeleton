"""
Fonctions de calcul des métriques d'évaluation, opérant sur le
format Trace défini dans trace_schema.py.
"""


def success_rate(trace, expected_output: dict) -> bool:

    """ Success Rate : Compare l'état final du système, reconstruit à partir de la
    trace, aux valeurs attendues (issues de evaluation_functions.
    system_level dans le schéma de scénario).
    """
    if not trace.events:
        return False
 
    etat_final_du_systeme = {}
    for evenement in trace.events:
        etat_final_du_systeme.update(evenement.output)
 
    return all(
        etat_final_du_systeme.get(cle) == valeur
        for cle, valeur in expected_output.items()
    )

def goal_condition_recall(trace, conditions: list) -> float:

    """Goal Condition Recall : Proportion des conditions nécessaires à l'accomplissement de
    l'objectif qui sont satisfaites.
    """
    if not conditions:
        return 1.0
    satisfaites = sum(1 for cond in conditions if cond(trace))
    return satisfaites / len(conditions)

def run_to_run_consistency(traces: list) -> float:
    """Run-to-run Consistency : proportion des exécutions (plusieurs
    Trace du MÊME scénario) qui aboutissent au résultat final le plus
    fréquent.
    """
    if len(traces) < 2:
        return 1.0

    resultats_finaux = []
    for trace in traces:
        etat_final = {}
        for e in trace.events:
            etat_final.update(e.output)
        resultats_finaux.append(str(sorted(etat_final.items())))

    occurrences = {}
    for resultat in resultats_finaux:
        occurrences[resultat] = occurrences.get(resultat, 0) + 1

    plus_frequent = max(occurrences.values())
    return plus_frequent / len(traces)


def latency(trace) -> float:
    """Latency : temps total de l'exécution,
    en secondes."""
    if not trace.events:
        return 0.0
    return trace.events[-1].timestamp

def cost(trace) -> dict:
    """Cost : Somme des tokens consommés au cours de l'exécution, à partir
    des métadonnées d'usage exposées par les agents (usage_metadata).
    """
    total_tokens = 0
    for e in trace.events:
        usage = e.output.get("usage_metadata")
        if usage and "total_tokens" in usage:
            total_tokens += usage["total_tokens"]

    return {"total_tokens": total_tokens}

def redundancy(trace) -> float:
    """Redundancy :la proportion d'événements dont la sortie est identique
    à une sortie déjà produite par le même agent plus tôt dans la
    même exécution — une répétition inutile.
    """
    if not trace.events:
        return 0.0

    deja_vus = {}
    redondants = 0

    for e in trace.events:
        historique = deja_vus.setdefault(e.node_name, [])
        if e.output in historique:
            redondants += 1
        historique.append(e.output)

    return redondants / len(trace.events)