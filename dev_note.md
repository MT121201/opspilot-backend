# Dev Note
## Rule:
- API layer does not touch SQLAlchemy models directly
- Business logic lives in services/
- DB session handling lives only in db/
  - Engine is global (one per process)
  - Session is per request