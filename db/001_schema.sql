-- Übrig Bern: Plattform-Schema (Supabase / Postgres)
-- Grundsatz: so wenig Tabellen wie möglich. Zwei Tabellen, eine Enum, drei Funktionen.
-- Zugriff ausschliesslich über RLS; Zustandswechsel einer Ausschreibung nur über RPC (Row-Lock).

create extension if not exists pgcrypto;

-- ---------- Profile (1:1 zu auth.users) ----------
create type public.role_t as enum ('kitchen', 'taker', 'admin');

create table public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  role        public.role_t not null default 'taker',
  org         text not null check (length(org) between 2 and 120),        -- Betrieb oder Organisation
  contact     text not null check (length(contact) between 2 and 120),    -- Name der Person
  phone       text not null check (length(phone) between 6 and 40),
  address     text check (length(address) <= 200),                        -- Übergabeort (Küche) / Sitz (Abnehmer)
  approved    boolean not null default false,                             -- Admin schaltet frei
  lang        text not null default 'de' check (lang in ('de','fr','it','en')),
  created_at  timestamptz not null default now()
);

-- ---------- Ausschreibungen ----------
create type public.offer_status_t as enum ('open', 'reserved', 'picked', 'cancelled', 'expired');

create table public.offers (
  id            uuid primary key default gen_random_uuid(),
  kitchen_id    uuid not null references public.profiles(id) on delete cascade,
  dish          text not null check (length(dish) between 2 and 140),
  portions      int  not null check (portions between 1 and 999),
  veg           boolean not null default false,
  vegan         boolean not null default false,
  no_pork       boolean not null default false,
  hot           boolean not null default false,
  allergens     smallint[] not null default '{}' check (allergens <@ array[1,2,3,4,5,6,7,8,9,10,11,12,13,14]::smallint[]),
  made_at       timestamptz not null,
  use_by        timestamptz not null,
  pickup_from   timestamptz not null,
  pickup_to     timestamptz not null,
  address       text not null check (length(address) between 3 and 200),
  note          text check (length(note) <= 300),
  check_ok      boolean not null default false,                           -- Freigabe-Check bestätigt
  status        public.offer_status_t not null default 'open',
  reserved_by   uuid references public.profiles(id) on delete set null,
  reserved_at   timestamptz,
  created_at    timestamptz not null default now(),
  constraint offers_window check (pickup_to > pickup_from and use_by >= pickup_from and made_at <= pickup_from)
);
create index offers_status_pickup_idx on public.offers (status, pickup_to);
create index offers_kitchen_idx on public.offers (kitchen_id);
create index offers_reserved_by_idx on public.offers (reserved_by);

-- ---------- Hilfsfunktionen ----------
create or replace function public.my_role() returns public.role_t
language sql stable security definer set search_path = public, pg_temp as
$$ select role from public.profiles where id = auth.uid() $$;

create or replace function public.i_am_approved() returns boolean
language sql stable security definer set search_path = public, pg_temp as
$$ select coalesce((select approved from public.profiles where id = auth.uid()), false) $$;

revoke all on function public.my_role() from public;
revoke all on function public.i_am_approved() from public;
grant execute on function public.my_role(), public.i_am_approved() to authenticated;
-- Supabase-Default-Privilegien geben EXECUTE auch an anon: explizit entziehen
revoke execute on function public.my_role(), public.i_am_approved() from anon;
alter default privileges in schema public revoke execute on functions from anon;

grant usage on schema public to authenticated;
grant select, insert, update on public.profiles to authenticated;
grant select, insert, update on public.offers to authenticated;

-- ---------- RLS ----------
alter table public.profiles enable row level security;
alter table public.offers   enable row level security;

-- Profile: eigenes sehen/anlegen/ändern; Admin sieht alle und darf approved/role setzen.
create policy profiles_select_own   on public.profiles for select to authenticated using (id = auth.uid());
create policy profiles_select_admin on public.profiles for select to authenticated using (public.my_role() = 'admin');
create policy profiles_insert_own   on public.profiles for insert to authenticated
  with check (id = auth.uid() and approved = false and role in ('kitchen','taker'));
-- WITH CHECK darf profiles nicht selbst abfragen (Rekursion) -> SECURITY-DEFINER-Helfer
create policy profiles_update_own   on public.profiles for update to authenticated
  using (id = auth.uid()) with check (id = auth.uid() and approved = public.i_am_approved() and role = public.my_role());
create policy profiles_update_admin on public.profiles for update to authenticated
  using (public.my_role() = 'admin') with check (public.my_role() = 'admin');

-- Freigegebene Abnehmer sehen, wer anbietet (Betrieb, Kontakt, Telefon) – aber nur bei Ausschreibungen, die sie sehen dürfen.
create policy profiles_select_counterpart on public.profiles for select to authenticated
  using (
    public.i_am_approved() and exists (
      select 1 from public.offers o
      where (o.kitchen_id = profiles.id and (o.status = 'open' or o.reserved_by = auth.uid()))
         or (o.reserved_by = profiles.id and o.kitchen_id = auth.uid())
    )
  );

-- Ausschreibungen
create policy offers_select_open on public.offers for select to authenticated
  using (public.i_am_approved() and status = 'open' and pickup_to > now());
create policy offers_select_mine on public.offers for select to authenticated
  using (kitchen_id = auth.uid() or reserved_by = auth.uid() or public.my_role() = 'admin');
create policy offers_insert_kitchen on public.offers for insert to authenticated
  with check (kitchen_id = auth.uid() and public.my_role() = 'kitchen' and public.i_am_approved() and status = 'open' and reserved_by is null);
create policy offers_update_kitchen on public.offers for update to authenticated
  using (kitchen_id = auth.uid()) with check (kitchen_id = auth.uid() and reserved_by is not distinct from (select reserved_by from public.offers x where x.id = offers.id));
-- Reservieren/Freigeben/Abholen NUR über RPC (unten), keine direkte Update-Policy für Abnehmer.

-- ---------- Zustandswechsel mit Row-Lock ----------
create or replace function public.reserve_offer(p_offer uuid) returns public.offers
language plpgsql security definer set search_path = public, pg_temp as $$
declare o public.offers;
begin
  if private.my_role() <> 'taker' or not private.i_am_approved() then raise exception 'not_allowed'; end if;
  select * into o from public.offers where id = p_offer for update;
  if not found then raise exception 'not_found'; end if;
  if o.status <> 'open' or o.pickup_to <= now() then raise exception 'not_open'; end if;
  update public.offers set status = 'reserved', reserved_by = auth.uid(), reserved_at = now() where id = p_offer returning * into o;
  return o;
end $$;

create or replace function public.release_offer(p_offer uuid) returns public.offers
language plpgsql security definer set search_path = public, pg_temp as $$
declare o public.offers;
begin
  select * into o from public.offers where id = p_offer for update;
  if not found then raise exception 'not_found'; end if;
  if o.status <> 'reserved' then raise exception 'not_reserved'; end if;
  if o.reserved_by <> auth.uid() and o.kitchen_id <> auth.uid() and private.my_role() <> 'admin' then raise exception 'not_allowed'; end if;
  update public.offers set status = 'open', reserved_by = null, reserved_at = null where id = p_offer returning * into o;
  return o;
end $$;

create or replace function public.mark_picked(p_offer uuid) returns public.offers
language plpgsql security definer set search_path = public, pg_temp as $$
declare o public.offers;
begin
  select * into o from public.offers where id = p_offer for update;
  if not found then raise exception 'not_found'; end if;
  if o.status <> 'reserved' then raise exception 'not_reserved'; end if;
  if o.reserved_by <> auth.uid() and o.kitchen_id <> auth.uid() then raise exception 'not_allowed'; end if;
  update public.offers set status = 'picked' where id = p_offer returning * into o;
  return o;
end $$;

revoke all on function public.reserve_offer(uuid), public.release_offer(uuid), public.mark_picked(uuid) from public;
grant execute on function public.reserve_offer(uuid), public.release_offer(uuid), public.mark_picked(uuid) to authenticated;
revoke execute on function public.reserve_offer(uuid), public.release_offer(uuid), public.mark_picked(uuid) from anon;

-- ---------- Realtime für die Live-Liste ----------
alter publication supabase_realtime add table public.offers;
alter publication supabase_realtime add table public.profiles;

-- ---------- Ablauf: offene Ausschreibungen nach Abholfenster als 'expired' lesen ----------
-- (kein Cron nötig: die Select-Policy blendet abgelaufene aus; die Küche sieht sie in "Meine" weiterhin.)

-- ---------- Nachtrag 25.09.2026: Helfer aus der API nehmen ----------
-- Schema "private" ist für PostgREST unsichtbar; Policies folgen dem Umzug (OID-Referenz).
-- In den RPCs heissen die Aufrufe danach private.my_role() / private.i_am_approved().
create schema if not exists private;
grant usage on schema private to authenticated;
alter function public.my_role() set schema private;
alter function public.i_am_approved() set schema private;
revoke execute on function public.reserve_offer(uuid), public.release_offer(uuid), public.mark_picked(uuid) from anon, public;
