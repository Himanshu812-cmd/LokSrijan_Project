"""Business logic.

Services hold the logic; routers only validate input and call a service. One
file per concern, e.g. ``challenge_service.py``, ``ai_service.py``,
``matching_service.py``.

A service receives a database session as an argument rather than opening its
own, so the request lifecycle stays in one place (``get_db``) and services stay
testable without a running server.

Two project rules apply here and not in the routers:
    - AI output is returned with its reasoning, never as a bare score.
    - AI suggests; a human validates. A service must not finalise an important
      decision on its own.

Nothing is implemented yet.
"""
