# TODO

What is still open after the 2026-11 cleanup. Background and evidence for each item: [PROJECT_AUDIT.md](PROJECT_AUDIT.md) sections 3-4.

## Product

- [x] **Identity / auth decision.** Anonymous device identity: the web app keeps a random `X-Device-Id` in localStorage and the API derives `owner_id`/`user_id` from it (`get_current_user` in `api/src/db/deps.py`). Groups, templates, payments and analytics are scoped to that user.
- [ ] **Real login.** Device identity is lost when site data is cleared or on another device, and the shared API key still ships in the bundle. Upgrade path: sign-in that links device ids to an account.
- [ ] **Group members are name-only.** People added to a group become `users` rows with no device id; they cannot open the group themselves. Needs invite links or login.
- [ ] **Real reminders / notifications.** "Send reminder" is a fake success message; the notification and sound toggles are stored but nothing reads them.
- [ ] **Multi-device sync.** Splits and history live in one browser's IndexedDB.

## Infra follow-ups

- [ ] CI web image build needs a repository variable `VITE_FASTAPI_API_URL` and a secret `VITE_API_KEY` in the `master` environment.
