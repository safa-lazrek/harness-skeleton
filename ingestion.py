import sys
import time
sys.path.append(".")
from trace_schema import Trace, TraceEvent


def ingest(app, initial_state: dict, run_id: str) -> Trace:
    trace = Trace(run_id=run_id)
    debut = time.time()

    for step_number, step in enumerate(app.stream(initial_state), start=1):
        maintenant = time.time()
        for node_name, output in step.items():
            trace.events.append(
                TraceEvent(
                    step_number=step_number,
                    node_name=node_name,
                    output=output,
                    timestamp=maintenant - debut,
                )
            )

    return trace