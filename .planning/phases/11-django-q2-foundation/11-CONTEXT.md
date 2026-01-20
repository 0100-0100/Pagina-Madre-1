# Phase 11: Django-Q2 Foundation - Context

**Gathered:** 2026-01-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Set up Django-Q2 task queue infrastructure with SQLite-safe configuration. This is the foundation that enables background task processing for later phases. Includes WAL mode, single worker configuration, admin integration, and verification that tasks execute successfully.

</domain>

<decisions>
## Implementation Decisions

### Infrastructure Approach
- SQLite + ORM broker for v1.3 (sufficient for <100 users)
- Single worker process (SQLite concurrency constraint)
- WAL mode enabled to prevent database locking
- Document upgrade path to PostgreSQL + Redis for future scaling

### Admin Monitoring
- Detailed task monitoring in Django admin (duration, retry count, error details)
- Separate views for queued/scheduled tasks vs completed tasks
- Filter available for failed tasks (not highlighted at top)
- All standard Django-Q2 admin models registered

### Development Workflow
- Run qcluster in separate terminal alongside runserver
- Tasks always run async (must run worker to test — no sync mode)
- Verbose logging when DEBUG=True, minimal in production

### Claude's Discretion
- Exact Q_CLUSTER configuration values (beyond documented timeout=120, retry=180)
- Admin list_display column order
- Log formatting details

</decisions>

<specifics>
## Specific Ideas

- Include documentation comments in settings.py explaining how to upgrade to PostgreSQL + Redis
- The upgrade path should mention: install redis/valkey, change broker to redis, scale workers

</specifics>

<deferred>
## Deferred Ideas

- PostgreSQL migration — defer until scale requires it
- Redis/Valkey integration — defer until scale requires it
- Multi-worker configuration — requires different database

</deferred>

---

*Phase: 11-django-q2-foundation*
*Context gathered: 2026-01-19*
