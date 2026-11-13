from math import comb  # comb(a, b) = nombre de façons de choisir b éléments parmi a
import json
from ingestion import ingest

# ---------------------------------------------------------------
# SUCCESS RATE 
# ---------------------------------------------------------------
def compute_success_rate(resultats):
    n_a = sum(resultats)   # nombre de tâches réussies
    n = len(resultats)     # nombre total de tâches
    return n_a / n if n else 0.0
def run_success_rate(app, chemin_json="scenario.json"):
    scenario = json.load(open(chemin_json))["scenario"]

    resultats = []
    for agent in scenario["agents"]:
        for p in agent.get("prompts", []):
            # 1. envoyer la question au système
            trace_id, reponse = ingest(app, {"input": p["prompt"]}, agent["id"])

            # 2. la bonne réponse écrite dans le JSON
            bonne_reponse = p.get("answer", p.get("expected-value"))

            # 3. corriger : 1 ou 0
            if str(bonne_reponse) in str(reponse):
                resultats.append(1)
            else:
                resultats.append(0)

    # 4. calculer
    return compute_success_rate(resultats)


# ---------------------------------------------------------------
# CONSISTENCY : lancer les essais (pour pass^k)
# ---------------------------------------------------------------
def lancer_essais(app, chemin_json="scenario.json", num_trials=4):
    scenario = json.load(open(chemin_json))["scenario"]

    results = []
    for agent in scenario["agents"]:
        for i, p in enumerate(agent.get("prompts", [])):
            task_id = f"{agent['id']}-{i}"
            bonne_reponse = p.get("answer", p.get("expected-value"))

            for trial in range(num_trials):
                # TODO : vider la mémoire des agents ici (avant chaque essai)
                trace_id, reponse = ingest(app, {"input": p["prompt"]}, f"{task_id}-t{trial}")
                reussi = bonne_reponse is not None and str(bonne_reponse) in str(reponse)
                results.append({"task_id": task_id, "trial": trial,
                                "reward": 1.0 if reussi else 0.0})
    return results


# ---------------------------------------------------------------
# CONSISTENCY : pass^k  (Yao et al., 2024, section 3)
# ---------------------------------------------------------------
def compute_pass_hat_k(results):                                                                                                  





    # --- Bloc 1 : savoir si un essai est réussi ---
    def is_successful(reward):
        return (1 - 1e-6) <= reward <= (1 + 1e-6)

    # --- Bloc 2 : num_trials, le nombre d'essais par tâche ---
    num_trials = len(set([r["trial"] for r in results]))

    # --- Bloc 3 : c, le nombre de réussites de chaque tâche ---
    c_per_task_id = {}
    for result in results:
        if result["task_id"] not in c_per_task_id:
            c_per_task_id[result["task_id"]] = 1 if is_successful(result["reward"]) else 0
        else:
            c_per_task_id[result["task_id"]] += 1 if is_successful(result["reward"]) else 0

    # --- Bloc 4 : pass^k pour chaque k de 1 à num_trials ---
    pass_hat_ks = {}
    for k in range(1, num_trials + 1):
        sum_task_pass_hat_k = 0
        for c in c_per_task_id.values():
            sum_task_pass_hat_k += comb(c, k) / comb(num_trials, k)
        pass_hat_ks[k] = sum_task_pass_hat_k / len(c_per_task_id)

    return pass_hat_ks



# ---------------------------------------------------------------
# GOAL CONDITION RECALL (GCR)
# Formule : GCR = 1 - |S_GT \ S_E| / |S_GT|
#   S_GT = conditions attendues (les sous-tâches du JSON)
#   S_E  = conditions atteintes (les sous-tâches terminées par le système)
# Sources : ProgPrompt (Singh et al., 2023), section C "Evaluation Metrics"
#           SMART-LLM (Kannan et al., 2023), section D "Evaluation Metrics"
# ---------------------------------------------------------------
def compute_gcr(attendues, atteintes):
    S_GT = set(attendues)                       # conditions attendues
    S_E = set(atteintes)                        # conditions atteintes
    non_atteintes = S_GT - S_E                  # attendues mais pas atteintes
    return 1 - len(non_atteintes) / len(S_GT) if S_GT else 0.0


def run_gcr(app, chemin_json="scenario.json"):
    scenario = json.load(open(chemin_json))["scenario"]

    # 1. les conditions attendues : les sous-tâches du JSON (on ignore les id vides)
    attendues = [s["id"] for s in scenario["task_decomposition"]["subtasks"] if s.get("id")]

    scores = []
    for agent in scenario["agents"]:
        for p in agent.get("prompts", []):
            # 2. envoyer la question au système
            trace_id, reponse = ingest(app, {"input": p["prompt"]}, agent["id"])

            # 3. les conditions atteintes : les sous-tâches terminées par le système
            # TODO : à adapter selon où le système indique ses sous-tâches terminées
            atteintes = reponse.get("subtasks_done", []) if isinstance(reponse, dict) else []

            # 4. GCR de cette question
            scores.append(compute_gcr(attendues, atteintes))

    # 5. moyenne sur toutes les questions
    return sum(scores) / len(scores) if scores else 0.0