from math import comb  # comb(a, b) = nombre de façons de choisir b éléments parmi a

def compute_success_rate(results, en_pourcentage=False):
    # --- Bloc 1 : compter n_a, le nombre de tâches réussies ---
    n_a = sum(1 for r in results if r.success)

    # --- Bloc 2 : compter n, le nombre total de tâches ---
    n = len(results)

    # --- Bloc 3 : TSR = n_a / n ---
    success_rate = n_a / n

    # --- Bloc 4 : choisir le format ---
    if en_pourcentage:
        return success_rate * 100
    return success_rate

def compute_pass_hat_k(results):
    """
    Calcule pass^k (cohérence entre exécutions), même méthode que tau-bench (run.py, display_metrics).
    Formule (Yao et al., 2024, section 3) : pass^k = moyenne sur les tâches de C(c, k) / C(n, k)

    results : liste des essais. Chaque essai a :
        - task_id : identifiant de la tâche
        - trial   : numéro de l'essai (0, 1, 2...)
        - reward  : 1.0 si réussi, 0.0 si raté

    Renvoie : un dictionnaire {k: score}, par exemple {1: 0.667, 2: 0.444, 3: 0.333}
    """

    # --- Bloc 1 : savoir si un essai est réussi ---
    # Renvoie True si reward vaut 1.
    # La marge 1e-6 évite les erreurs d'arrondi (0.9999999 compte comme 1).
    def is_successful(reward):
        return (1 - 1e-6) <= reward <= (1 + 1e-6)

    # --- Bloc 2 : trouver n, le nombre d'essais par tâche ---
    # On récupère tous les numéros d'essai, on garde chaque numéro une seule fois (set),
    # puis on les compte. Exemple : essais 0, 1, 2 -> n = 3.
    num_trials = len(set([r.trial for r in results]))

    # --- Bloc 3 : compter c, le nombre de réussites de chaque tâche ---
    # Résultat : un dictionnaire {task_id: nombre de réussites}, par exemple {1: 3, 2: 2, 3: 1}.
    c_per_task_id = {}
    for result in results:
        if result.task_id not in c_per_task_id:
            # Première fois qu'on voit cette tâche : on crée son compteur (1 si réussi, 0 sinon)
            c_per_task_id[result.task_id] = 1 if is_successful(result.reward) else 0
        else:
            # Tâche déjà vue : on ajoute 1 si l'essai est réussi, 0 sinon
            c_per_task_id[result.task_id] += 1 if is_successful(result.reward) else 0

    # --- Bloc 4 : calculer pass^k pour chaque k de 1 à n ---
    pass_hat_ks = {}
    for k in range(1, num_trials + 1):
        sum_task_pass_hat_k = 0  # total des scores des tâches, remis à zéro pour chaque k

        for c in c_per_task_id.values():
            # Formule pour UNE tâche : C(c, k) / C(n, k)
            # = probabilité que k essais tirés au hasard parmi les n soient tous réussis
            sum_task_pass_hat_k += comb(c, k) / comb(num_trials, k)

        # Moyenne sur toutes les tâches = pass^k
        pass_hat_ks[k] = sum_task_pass_hat_k / len(c_per_task_id)

    return pass_hat_ks