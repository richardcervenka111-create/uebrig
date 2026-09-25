-- 003_bootstrap_admin (applied live 25. 9. 2026 via MCP apply_migration)
-- The first admin. Richard's profile was created by his first magic-link login
-- (25. 9. 2026 01:10 UTC) as kitchen/unapproved; only an admin can approve others,
-- so the very first admin has to be set from the database side.
-- Looked up by e-mail, never by a generated id. Not destructive, idempotent.
update public.profiles
   set role = 'admin', approved = true
 where id = (select id from auth.users where email = 'richard.cervenka@icloud.com');
