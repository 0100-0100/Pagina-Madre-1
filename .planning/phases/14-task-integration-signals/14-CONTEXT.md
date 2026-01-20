# Phase 14: Task Integration + Signals - Context

**Gathered:** 2026-01-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Connect the Playwright scraper (Phase 13) to Django-Q2 (Phase 11) via post_save signals. Census lookup auto-triggers on user registration and retries on transient failures. Manual refresh is handled in Phase 15.

</domain>

<decisions>
## Implementation Decisions

### Signal timing
- Queue task immediately after registration transaction commits (transaction.on_commit)
- Trigger only on new user creation, not on user updates
- No extra rate limiting at signal level — scraper's 5s limit is sufficient
- Queued tasks persist — auto-process when qcluster starts (no expiration)

### Retry behavior
- Maximum 3 attempts (initial + 2 retries)
- Exponential backoff: 1 minute, 5 minutes, 15 minutes
- Retry all errors except clear results (found, not_found, cancelled are permanent)
- Retriable: timeout, connection error, captcha_failed, blocked
- Retry count hidden from user — just show status

### Status updates
- PENDING when task first queued
- SCRAPING when browser is actively running
- RETRYING status with timestamp on each retry attempt
- Add retry_count field to CedulaInfo model to track attempts

### Error handling
- ERROR status after all retries exhausted
- Store error details in existing raw_response field (TextField for debug storage)
- Log errors only — no admin notifications
- Only leaders can trigger manual retry (consistent with RBAC model)

### Claude's Discretion
- Exact logging format and verbosity
- Task function naming and module organization
- Signal handler registration approach (decorators vs manual)

</decisions>

<specifics>
## Specific Ideas

- Use transaction.on_commit() to ensure task queues after user is fully saved
- Leverage Django-Q2's built-in retry mechanism if available, otherwise implement manually
- Status progression: PENDING → SCRAPING → (RETRYING →)* → FOUND/NOT_FOUND/CANCELLED/ERROR

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 14-task-integration-signals*
*Context gathered: 2026-01-20*
