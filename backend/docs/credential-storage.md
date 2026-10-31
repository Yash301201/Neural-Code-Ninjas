# Passwords and JWT authentication

Your edited `.local/portal-credentials.json` is the local password input/reference file. Changing it alone does not update MySQL. From the backend folder run:

```powershell
.\.venv\Scripts\python.exe -m scripts.sync_portal_credentials
```

The script validates all four account identities before writing, applies the exact password strings using Argon2id, and synchronizes `.local/portal-logins.txt`. It leaves your JSON unchanged. The old `scripts.set_local_demo_passwords` command now delegates to this sync command and no longer restores hardcoded passwords.

`users.email`, `users.role`, and `users.password_hash` are stored in MySQL `learnpath_ai`. Passwords are not stored inside JWTs. The private local JSON/text copies contain readable passwords for your local reference; keep them out of Git and frontend assets.

The existing `JWT_SECRET` in backend/.env signs login tokens with HS256. One application signing key is shared across account roles. Login validates the password hash, creates a token containing the user ID (`sub`) and expiry (`exp`), and protected endpoints verify the signature/expiry and load the current role from MySQL. No new per-user key is needed. The existing signing secret is preserved.

Show the evaluator this query and `app/security.py`, without exposing .env secrets:

```sql
SELECT email,role,password_hash FROM learnpath_ai.users
WHERE email IN ('admin@learnpath.dev','hod@learnpath.dev',
               'faculty@learnpath.dev','student@learnpath.dev');
```

Edit Python `.py` source files. Files under `__pycache__` ending `.pyc` are automatically generated binary caches and are not configuration files.
