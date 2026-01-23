# Dev Note
## Rule:
- API layer does not touch SQLAlchemy models directly
- Business logic lives in services/
- DB session handling lives only in db/
  - Engine is global (one per process)
  - Session is per request


## Ticket Idempotency
- We “claim” the key before creating the ticket. That prevents duplicates under retries.
- We commit claim early so concurrent requests see it.
- We detect misuse: same key and different payload → 409.