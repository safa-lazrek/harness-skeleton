from langfuse_config import langfuse
from langfuse import observe


@observe(capture_output=False)
def ingest(app, initial_state: dict, run_id: str):
    """Exécute un système multi-agent et observe son exécution via
    Langfuse. Renvoie l'identifiant de la trace (pour la consulter
    sur Langfuse) et le résultat final de l'exécution."""
    resultat = app.invoke(initial_state)
    langfuse.update_current_span(output=resultat)
    langfuse.flush()
    trace_id = langfuse.get_current_trace_id()
    return trace_id, resultat