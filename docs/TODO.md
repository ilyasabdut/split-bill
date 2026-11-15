# TODO

What is still open after the 2026-11 cleanup. Background and evidence for each item: [PROJECT_AUDIT.md](PROJECT_AUDIT.md) sections 3-4.

## Product

- [ ] **Identity / auth decision.** The frontend hardcodes `owner_id: 1` / `user_id: 1` and ships one shared API key in the bundle. Decide: anonymous-by-link (drop `users`, groups by share code) or real sign-up/login with per-user authorisation.
- [ ] **Real reminders / notifications.** "Send reminder" is a fake success message; the notification and sound toggles are stored but nothing reads them.
- [ ] **Server-side payments.** `api/src/routers/payments.py` works, but the frontend keeps payment state in IndexedDB only.
- [ ] **Multi-device sync.** Splits and history live in one browser's IndexedDB.
- [ ] **E2E tests.** None exist.

## Infra follow-ups

- [ ] CI web image build needs a repository variable `VITE_FASTAPI_API_URL` and a secret `VITE_API_KEY` in the `master` environment.
