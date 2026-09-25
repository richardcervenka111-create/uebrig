-- Übrig Bern: 002_hardening (25.09.2026)
-- Drei Lücken aus dem Architektur-Review von 001_schema.sql, ohne Änderung an der App:
--  (1) Helfer-Aufrufe in Policies als (select …) — Advisor-Lint 0003, Ergebnis wird pro Statement gecacht.
--  (2) offers_update_kitchen pinnte nur reserved_by: die Küche konnte status='picked'/'expired' direkt setzen
--      und die RPC-Zustandsmaschine umgehen. Neu: Policy erlaubt nur open/reserved → open/reserved/cancelled,
--      ein BEFORE-UPDATE-Trigger pinnt kitchen_id, reserved_by, reserved_at, created_at für Clients
--      (RPCs laufen als Funktionsbesitzer und bleiben unberührt).
--  (3) profiles_select_counterpart lief ein korreliertes EXISTS auf offers (selbst unter RLS) — ersetzt durch
--      SECURITY-DEFINER-Helfer private.can_see_profile(uuid). Sichtbarkeit unverändert: Betrieb/Kontakt der
--      Küche bei offenen Angeboten und der Gegenpartei nach Reservation (die App liest genau das).

-- ---------- (3) Helfer ----------
create or replace function private.can_see_profile(p uuid) returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (
    select 1 from public.offers o
    where (o.kitchen_id = p and ((o.status = 'open' and o.pickup_to > now()) or o.reserved_by = (select auth.uid())))
       or (o.reserved_by = p and o.kitchen_id = (select auth.uid()))
  )
$$;
revoke all on function private.can_see_profile(uuid) from public, anon;
grant execute on function private.can_see_profile(uuid) to authenticated;

-- ---------- (2) Trigger-Wächter ----------
create or replace function private.offers_guard_update() returns trigger
language plpgsql set search_path = '' as $$
begin
  -- Nur direkte Client-Updates prüfen; SECURITY-DEFINER-RPCs laufen als Funktionsbesitzer.
  if current_user in ('authenticated', 'anon') then
    if new.kitchen_id <> old.kitchen_id
       or new.reserved_by is distinct from old.reserved_by
       or new.reserved_at is distinct from old.reserved_at
       or new.created_at <> old.created_at then
      raise exception 'not_allowed' using hint = 'kitchen_id/reserved_by/reserved_at nur per RPC';
    end if;
    if new.status <> old.status and new.status <> 'cancelled' then
      raise exception 'not_allowed' using hint = 'Statuswechsel nur per RPC; direkt nur Stornieren';
    end if;
    if old.status in ('picked', 'cancelled', 'expired') then
      raise exception 'not_allowed' using hint = 'abgeschlossene Angebote sind unveränderlich';
    end if;
  end if;
  return new;
end $$;
revoke all on function private.offers_guard_update() from public, anon;
grant execute on function private.offers_guard_update() to authenticated;
drop trigger if exists offers_guard_update on public.offers;
create trigger offers_guard_update before update on public.offers
  for each row execute function private.offers_guard_update();

-- ---------- (1)+(2)+(3) Policies neu ----------
drop policy if exists profiles_select_own on public.profiles;
drop policy if exists profiles_select_admin on public.profiles;
drop policy if exists profiles_insert_own on public.profiles;
drop policy if exists profiles_update_own on public.profiles;
drop policy if exists profiles_update_admin on public.profiles;
drop policy if exists profiles_select_counterpart on public.profiles;

create policy profiles_select_own on public.profiles for select to authenticated
  using (id = (select auth.uid()));
create policy profiles_select_admin on public.profiles for select to authenticated
  using ((select private.my_role()) = 'admin');
create policy profiles_insert_own on public.profiles for insert to authenticated
  with check (id = (select auth.uid()) and approved = false and role in ('kitchen', 'taker'));
create policy profiles_update_own on public.profiles for update to authenticated
  using (id = (select auth.uid()))
  with check (id = (select auth.uid()) and approved = (select private.i_am_approved()) and role = (select private.my_role()));
create policy profiles_update_admin on public.profiles for update to authenticated
  using ((select private.my_role()) = 'admin') with check ((select private.my_role()) = 'admin');
create policy profiles_select_counterpart on public.profiles for select to authenticated
  using ((select private.i_am_approved()) and private.can_see_profile(id));

drop policy if exists offers_select_open on public.offers;
drop policy if exists offers_select_mine on public.offers;
drop policy if exists offers_insert_kitchen on public.offers;
drop policy if exists offers_update_kitchen on public.offers;

create policy offers_select_open on public.offers for select to authenticated
  using ((select private.i_am_approved()) and status = 'open' and pickup_to > now());
create policy offers_select_mine on public.offers for select to authenticated
  using (kitchen_id = (select auth.uid()) or reserved_by = (select auth.uid()) or (select private.my_role()) = 'admin');
create policy offers_insert_kitchen on public.offers for insert to authenticated
  with check (kitchen_id = (select auth.uid()) and (select private.my_role()) = 'kitchen'
              and (select private.i_am_approved()) and status = 'open' and reserved_by is null);
create policy offers_update_kitchen on public.offers for update to authenticated
  using (kitchen_id = (select auth.uid()) and status in ('open', 'reserved'))
  with check (kitchen_id = (select auth.uid()) and status in ('open', 'reserved', 'cancelled'));

-- Rollback (002_down): Policies aus 001_schema.sql wörtlich wiederherstellen, Trigger und
-- private.can_see_profile droppen. Nicht destruktiv: keine Daten, keine Spalten betroffen.
