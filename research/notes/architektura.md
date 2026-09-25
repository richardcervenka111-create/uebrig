# Übrig — Architecture research notes (multi-city, multi-country, no rewrite)

*Written 2026-09-25. Grounded on the current repo (`/home/user/uebrig/db/001_schema.sql`, 164 lines; `app/index.html`, 43 844 B / 392 lines; `app/config.js`; `README.md`) and on 26 Supabase documentation pages retrieved via `search_docs`. Every number that comes from a doc is cited inline. Anything not covered by a doc is marked **[experience, verify]**. Prices are quoted in USD as the docs give them; CHF conversions are estimates.*

## 0. Where we stand (measured, not remembered)

- **Schema:** two tables (`profiles` 1:1 to `auth.users`, `offers` keyed by `kitchen_id → profiles.id`), two enums (`role_t` = kitchen/taker/admin, `offer_status_t`), three SECURITY DEFINER RPCs with `FOR UPDATE` row-lock (`reserve_offer`, `release_offer`, `mark_picked`), helpers `my_role()` / `i_am_approved()` moved to schema `private` on 25.9. RLS on both tables; both tables in the `supabase_realtime` publication.
- **App:** single file, supabase-js 2.86.0 UMD from jsDelivr, `signInWithOtp` magic link, `postgres_changes` on `offers` with no filter → reloads board on any change, DE/FR/EN dictionaries in one object `I18N`, `lang` persisted in `localStorage`, `Notification` API only while the page is open.
- **Platform:** Free plan, `eu-west-3` (Paris), Nano compute. Project pauses after 7 days of low activity on Free ([Production checklist](https://supabase.com/docs/guides/deployment/going-into-prod), [Project pausing](https://supabase.com/docs/guides/platform/free-project-pausing)); restorable for 90 days.
- **Things in the current schema that the roadmap below must fix (found while reading, not assumed):**
  1. `offers_update_kitchen` `WITH CHECK` only pins `reserved_by`; a kitchen can set `status='picked'` or `'expired'` directly, bypassing the RPC state machine. Add `status` to the check (only `open→cancelled` allowed via direct update) or route cancel through an RPC too.
  2. `profiles_select_counterpart` runs a correlated `EXISTS` on `offers` — which itself has RLS — inside a policy on `profiles`. Nested RLS is exactly the pattern the RLS performance guide says to replace with a SECURITY DEFINER helper ([RLS performance](https://supabase.com/docs/guides/troubleshooting/rls-performance-and-best-practices-Z5Jjwv), tip 4).
  3. Policies call `public.i_am_approved()` / `public.my_role()` bare, not as `(select …)`. Lint `0003_auth_rls_initplan` will flag this; wrapping caches the result per statement ([Lint 0003](https://supabase.com/docs/guides/observability/advisors?queryGroups=lint&lint=0003_auth_rls_initplan)).
  4. `lang in ('de','fr','it','en')` and `allergens <@ array[1..14]` are hard-coded jurisdiction facts — both move to the ruleset tables in §3.
  5. `address text` on both tables is the only location concept; §2 replaces it with `sites`.
  6. `profiles` in the realtime publication means every profile change fans out an RLS check per subscriber (Postgres Changes limitation, see §5). Harmless at Bern scale, remove before city 2.

---

## 1. Tenancy model

### Recommendation
Three-level hierarchy, **one Supabase project, shared schema, tenant columns on every row**:

```
cities (Standort)  1─n  organisations  1─n  sites (Küche / Abgabestelle)
                              1─n  memberships (user × org × role)
offers.site_id → sites;  offers.org_id, offers.city_id denormalised (trigger-filled)
handover_events.offer_id → offers;  + org_id, city_id denormalised
```

- `cities` **is a table with config**: `id`, `slug` (`bern`, `zuerich`, `wien`), `country` (ISO-3166-1), `timezone` (IANA), `default_locale`, `locales text[]`, `currency`, `ruleset_key` (→ §3), `theme jsonb` (→ §9), `features jsonb` (feature flags per city), `status` (`planned|pilot|live|closed`), `centre geography(Point)`, `bbox`.
- **Every business row carries both `org_id` and `city_id`.** `org_id` is the security boundary (RLS), `city_id` is the operational boundary (moderation, stats, partitioning, white-label). Both are set by a `BEFORE INSERT` trigger from `site_id`, never trusted from the client.
- RLS authorisation goes through **two SECURITY DEFINER helpers in `private`**, each wrapped in `(select …)` in the policy:

```sql
create function private.my_org_ids() returns uuid[]
language sql stable security definer set search_path = '' as $$
  select coalesce(array_agg(org_id), '{}') from public.memberships
  where user_id = (select auth.uid()) and status = 'active' $$;

create function private.my_city_roles() returns table(city_id uuid, role text)
language sql stable security definer set search_path = '' as $$
  select city_id, role from public.city_roles where user_id = (select auth.uid()) $$;

-- policy shape used everywhere:
create policy offers_select_org on public.offers for select to authenticated
  using ( org_id = any (array(select private.my_org_ids())) );
```

  The `= any(array(select fn()))` form is the one the docs benchmark at 2–24 ms on a 1 M-row table **with an index on the tenant column**, versus timeouts without the wrap ([RLS performance](https://supabase.com/docs/guides/troubleshooting/rls-performance-and-best-practices-Z5Jjwv), section "Added example"). So: `create index on offers (org_id)`, `(city_id, status, pickup_to)`, `(site_id)`.
- Client queries always add the filter the policy already implies (`.eq('city_id', …)`), because "policies are implicit where clauses" and the planner needs the explicit filter ([RLS guide → Add filters](https://supabase.com/docs/guides/database/postgres/row-level-security)).
- Policies always name `to authenticated` (or `to anon` explicitly for the public stats views) — stops `anon` evaluation before any function call ([RLS guide → Specify roles](https://supabase.com/docs/guides/database/postgres/row-level-security)).

### Why not schema-per-tenant or project-per-city
- The docs do not describe schema-per-tenant as a Supabase pattern; the multi-tenant material that exists (SAML `sso_provider_id` per tenant with restrictive RLS, pgTAP "complex organizations" example) is all **shared-schema, tenant-column** ([SSO SAML → RLS](https://supabase.com/docs/guides/auth/enterprise-sso/auth-sso-saml), [Advanced pgTAP](https://supabase.com/docs/guides/local-development/testing/pgtap-extended)).
- Project-per-city multiplies fixed cost: "Each project you launch increases your monthly Compute costs"; compute credits cover one Micro/Nano project only ([Compute usage](https://supabase.com/docs/guides/platform/manage-your-usage/compute)). It also breaks cross-city users (an NGO active in Bern and Biel), cross-city stats, and shared rulesets.
- Project-per-**country** stays on the table for data-residency reasons only (§6); the schema must therefore never assume a single `country` — it is a column on `cities`, and all config resolves `city → country → default`.

### Trade-offs
- Denormalised `city_id`/`org_id` on child rows = redundancy guarded by triggers and a pgTAP test that asserts `offers.city_id = sites.city_id` for every row. Accepted: it keeps every policy a single-column predicate.
- Array-of-orgs RLS degrades if a user belongs to thousands of orgs (docs: rethink above ~1 000–10 000 list items). Our users belong to 1–5 orgs. City moderators do not get orgs in the array; they get a separate `city_roles` predicate.
- A user in company mode vs personal mode: no "personal" context exists in Übrig (unlike Sautero); every user acts for an org. Individuals (a private taker) get a one-person org of `kind='individual'`. Keeps the model to one path.

### Migration path from today's profiles/offers (zero-downtime, dual-write)
1. **Additive migration (002):** create `cities` (seed `bern`), `organisations`, `sites`, `memberships`, `city_roles`. Add nullable `org_id`, `site_id`, `city_id` to `offers`. Add `org_id` to `profiles` (nullable).
2. **Backfill in the same transaction:** one org per existing profile (`name = profiles.org`, `kind = case role when 'kitchen' then 'kitchen' else 'taker' end`, `status = case approved when true then 'approved' else 'pending'`), one membership (`owner`), one site per kitchen profile from `profiles.address` (geocode later, `location` nullable at first), `offers.site_id/org_id/city_id` from the kitchen's org; existing `admin` profiles → `city_roles (bern, 'moderator')`.
3. **Compatibility layer:** keep `kitchen_id` and `reserved_by` as-is (they are still the *user* who acted — useful in the event log). Trigger `offers_fill_tenant` derives `org_id/site_id/city_id` when a legacy client inserts with only `kitchen_id` (from the user's single membership). Old app keeps working unchanged.
4. **New policies live alongside old ones** (permissive policies OR together). Add the org-based policies, run pgTAP proving old-shape and new-shape clients see identical rows, then drop the `kitchen_id = auth.uid()` policies in migration 004.
5. **Feature flag:** `cities.features->>'orgs_ui'` read once at boot via RPC `app_bootstrap(city_slug)`; the new UI (org switcher, site picker) renders only when true. Flip for Bern after pilot users are migrated.
6. **Finally (005, DESTRUCTIVE, explicit approval):** `set not null` on `offers.org_id/site_id/city_id`, drop `profiles.org/address`, keep `profiles.contact/phone/lang` as the *person* record.

### Sources
[RLS guide](https://supabase.com/docs/guides/database/postgres/row-level-security) · [RLS performance troubleshooting](https://supabase.com/docs/guides/troubleshooting/rls-performance-and-best-practices-Z5Jjwv) · [Lint 0003](https://supabase.com/docs/guides/observability/advisors?queryGroups=lint&lint=0003_auth_rls_initplan) · [Compute usage](https://supabase.com/docs/guides/platform/manage-your-usage/compute) · [Advanced pgTAP (multi-tenant example)](https://supabase.com/docs/guides/local-development/testing/pgtap-extended)

### Verify later
- Run `explain analyze` under `set local role authenticated` on `offers` after migration 004 with a synthetic 100 k-row load (docs give the recipe) — before city 2, not after.

---

## 2. Data model additions

### Recommendation

```sql
-- organisations
create table public.organisations (
  id uuid primary key default gen_random_uuid(),
  city_id uuid not null references public.cities(id),          -- home city
  kind text not null check (kind in ('kitchen','taker','both','individual')),
  name text not null check (length(name) between 2 and 120),
  legal_id text,                                               -- CHE-123.456.789 (UID) / FN / SIREN…
  legal_id_verified_at timestamptz, legal_id_source text,      -- 'zefix' | 'manual'
  status text not null default 'pending' check (status in ('pending','approved','blocked')),
  created_at timestamptz not null default now()
);
create table public.sites (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references public.organisations(id) on delete cascade,
  city_id uuid not null references public.cities(id),
  name text not null, address_line text not null, postal_code text, locality text,
  country char(2) not null,
  location extensions.geography(Point, 4326),                  -- PostGIS
  pickup_notes text check (length(pickup_notes) <= 300),
  is_active boolean not null default true
);
create index sites_geo on public.sites using gist (location);
create table public.memberships (
  user_id uuid not null references auth.users(id) on delete cascade,
  org_id uuid not null references public.organisations(id) on delete cascade,
  role text not null check (role in ('owner','staff')),
  status text not null default 'active' check (status in ('invited','active','removed')),
  primary key (user_id, org_id)
);
create table public.city_roles (
  user_id uuid references auth.users(id) on delete cascade,
  city_id uuid references public.cities(id) on delete cascade,
  role text not null check (role in ('moderator','platform_admin')),
  primary key (user_id, city_id)
);
```

PostGIS: enable into the `extensions` schema, store `geography(Point)`, GIST index, insert as `'POINT(lon lat)'` (longitude first), expose nearest-neighbour via an RPC using `<->` — the docs' `nearby_restaurants` pattern verbatim ([PostGIS](https://supabase.com/docs/guides/database/extensions/postgis)). Note the doc's warning: PostGIS ≥ 2.3 is **not relocatable** between schemas — pick `extensions` on first enable.

**Offers:** add `site_id`, `org_id`, `city_id`, `ruleset_id` (snapshot of the ruleset in force when published, §3), replace `allergens smallint[]` check with a FK-like check against the ruleset's allergen list (trigger), keep `kitchen_id`/`reserved_by` as *actor* columns.

**Handover protocol as append-only event log:**

```sql
create table public.handover_events (
  id bigint generated always as identity primary key,
  offer_id uuid not null references public.offers(id),
  org_id uuid not null, city_id uuid not null,                  -- trigger-filled
  event_type text not null check (event_type in
    ('published','reserved','released','handed_over','received','temp_checked',
     'cancelled','expired','disputed','note')),
  actor_id uuid not null default auth.uid(),
  actor_org_id uuid not null,                                   -- whose behalf
  occurred_at timestamptz not null default now(),
  payload jsonb not null default '{}',                          -- temp_c, container_count, signature_ref, allergens_confirmed, photo_path
  ruleset_id uuid not null,                                     -- rules in force at that moment
  prev_hash bytea, hash bytea not null,                         -- sha256(prev_hash || row) — tamper-evidence
  constraint payload_valid check (extensions.jsonb_matches_schema(
    '{"type":"object","properties":{"temp_c":{"type":"number"},"container_count":{"type":"integer","minimum":0}},"additionalProperties":true}', payload))
);
revoke update, delete, truncate on public.handover_events from authenticated, anon;
create trigger handover_events_immutable before update or delete on public.handover_events
  for each row execute function private.raise_immutable();
```

- Inserts only via RPCs (`record_handover(p_offer, p_type, p_payload)`), which also advance `offers.status`; the existing RPCs are rewritten to *emit an event* and derive status. `offers.status` becomes a cache of the last event — cheap to read, always reproducible.
- `pg_jsonschema` validates the `payload` per `event_type` (the check constraint pattern is exactly what the docs show) ([pg_jsonschema](https://supabase.com/docs/guides/database/extensions/pg_jsonschema)). Keep the schema in a `event_schemas` table keyed by `(event_type, version)` and validate in the trigger so schemas can evolve without `ALTER TABLE`.
- Signatures: store a hash of the signature image + path in a **private** Storage bucket `protocols`, folder `org_id/offer_id/…`, RLS on `storage.objects` using `(storage.foldername(name))[1] = any(array(select private.my_org_ids()::text[]))` ([Storage access control](https://supabase.com/docs/guides/storage/security/access-control), [helper functions](https://supabase.com/docs/guides/storage/schema/helper-functions)). Private buckets need signed URLs or a JWT download ([Buckets](https://supabase.com/docs/guides/storage/buckets/fundamentals)). Both counterparties (kitchen org and taker org) need read → the taker's org gets a row in `handover_access(offer_id, org_id)` written by the `reserved` event, and the storage policy joins through it via a `private.` helper.
- Both parties are food-business operators under CH law (README: "Bis zur Übergabe haftet der Betrieb") — the *receiving* side must be able to prove what it took over. Therefore the `received` event is written by the taker, the `handed_over` by the kitchen; a handover is "complete" only with both. Export (§9) renders both.

**Audit trail — three layers, each for a different question:**

| Question | Tool | Notes |
|---|---|---|
| "What happened to this offer, legally?" | `handover_events` (own table) | Business audit, exported to the parties, retained per §10 |
| "Who changed which row, including admins?" | own `audit_log` table filled by generic trigger on `organisations`, `memberships`, `city_roles`, `rulesets` (old/new jsonb, `auth.uid()`, `current_setting('request.headers')::json->>'x-forwarded-for'`) | Cheap, queryable, RLS-protected (moderators only) |
| "Which role ran which SQL against sensitive objects?" | `pgaudit` object logging via a dedicated no-login role granted `select` on `profiles`, `handover_events` | Goes to Postgres logs, not a table; retention follows plan log retention (**[verify]** per-plan log retention) ([PGAudit](https://supabase.com/docs/guides/database/extensions/pgaudit)) |
| Long-term log archive | Log Drains (Pro+, $60/mo per drain + events) | Only when a funder/regulator asks; "public alpha" status ([Log drain usage](https://supabase.com/docs/guides/platform/manage-your-usage/log-drains), [Features status](https://supabase.com/docs/guides/getting-started/features)) |

Do not use `pgaudit` session mode with `all` — the docs warn about volume; object mode on two tables is enough.

### Trade-offs
- Event-sourcing the offer state means two writes per transition; at ≤ 100 offers/day/city this is noise. The gain — a legally usable, hash-chained record — is the product.
- `handover_events` grows forever by design; §10 defines what is anonymised (payload PII, actor names) vs. kept (temperatures, times, counts).
- PostGIS geography on Nano compute is fine for k-NN over hundreds of sites; heavy isochrone/routing stays out (the map research already uses OSM offline).

### Sources
[PostGIS](https://supabase.com/docs/guides/database/extensions/postgis) · [pg_jsonschema](https://supabase.com/docs/guides/database/extensions/pg_jsonschema) · [Storage access control](https://supabase.com/docs/guides/storage/security/access-control) · [Storage helpers](https://supabase.com/docs/guides/storage/schema/helper-functions) · [Buckets](https://supabase.com/docs/guides/storage/buckets/fundamentals) · [PGAudit](https://supabase.com/docs/guides/database/extensions/pgaudit) · [Log drains](https://supabase.com/docs/guides/platform/manage-your-usage/log-drains) · [Postgres log config](https://supabase.com/docs/guides/database/postgres/postgres-log-config)

### Verify later
- Postgres log retention per plan (needed to decide whether pgaudit alone satisfies a cantonal inspector).
- Whether a hash-chained DB record is accepted as "Selbstkontrolle"-documentation by the Bern Kantonales Laboratorium — legal question, not technical.

---

## 3. Configuration per jurisdiction (rulesets)

### Recommendation
Table-driven, versioned, effective-dated, resolved `city → country → global`:

```sql
create table public.rulesets (
  id uuid primary key default gen_random_uuid(),
  scope text not null check (scope in ('global','country','city')),
  country char(2), city_id uuid references public.cities(id),
  version int not null,
  effective_from date not null, effective_to date,
  rules jsonb not null,                       -- validated by pg_jsonschema against ruleset_schema v1
  source text, note text,                     -- "LMG/HyV Art. …", link
  created_by uuid, created_at timestamptz default now(),
  check ((scope='country') = (country is not null) or scope='city'),
  check ((scope='city') = (city_id is not null))
);
create unique index rulesets_active on public.rulesets (scope, coalesce(country,''), coalesce(city_id,'00000000-0000-0000-0000-000000000000'), version);

create table public.allergen_lists (
  code text not null,                          -- 'EU14' | 'US9' | 'CH14'
  version int not null,
  items jsonb not null,                        -- [{"id":1,"key":"gluten","labels":{"de-CH":"Glutenhaltiges Getreide","fr-CH":"…"}}]
  effective_from date not null, effective_to date,
  primary key (code, version)
);
```

`rules` example (CH):

```json
{ "hot_min_c": 65, "cold_max_c": 5, "cool_down_max_minutes": 120, "reheat_core_min_c": 72,
  "allergen_list": "EU14", "max_hours_after_made": 24, "require_temp_at_handover": true,
  "require_receiver_signature": true, "label_fields": ["dish","made_at","use_by","allergens","kitchen"] }
```

- **Resolver** `private.active_ruleset(p_city uuid, p_at timestamptz default now())` merges global ← country ← city (`jsonb ||`, later wins) among rows where `effective_from <= p_at::date and (effective_to is null or effective_to > p_at::date)`. Returned `id` of the most specific row is what `offers.ruleset_id` / `handover_events.ruleset_id` snapshot.
- **Client never hard-codes thresholds.** `app_bootstrap(city_slug)` (anon-callable, returns no PII) returns `{city, ruleset, allergens, locales, theme, features}`; the Freigabe-Check renders its seven questions from `rules`. The existing README hygiene text ("heiss ≥ 65 °C oder innert 2 h auf ≤ 5 °C … ≥ 72 °C Kern") becomes the seed row for `country='CH'`.
- **Schema of `rules` is itself versioned** (`ruleset_schemas(version, schema jsonb)`), checked in a trigger with `jsonb_matches_schema` — a new key (e.g. US "time as public health control" 4 h rule) is a new schema version, not a code change ([pg_jsonschema](https://supabase.com/docs/guides/database/extensions/pg_jsonschema)).
- Currency, date formats, first weekday come from `cities.default_locale` + `Intl`, not from rulesets — they are presentation, not law.
- Editing rulesets: moderators with `role='platform_admin'` only; every change audited (§2 audit_log); `effective_from` must be ≥ today + 1 for non-admins to stop retroactive rewriting of what was in force.

### Why
EU-14 = CH-14 today, US has 9 (sesame added 2023), Austria adds nothing but different inspection wording; temperature thresholds differ (CH HyV 65 °C hot vs. EU-common 63 °C in UK, 60 °C in parts of the US). Snapshotting `ruleset_id` on the event is what makes a 2027 export say "at the time, the rule was X".

### Trade-offs
- jsonb rules are less type-safe than columns; the pg_jsonschema check plus a pgTAP test per seed row compensates. Columns would force a migration per jurisdiction — the thing we are avoiding.
- Merge semantics (`||` is shallow) — keep `rules` flat by convention; the schema enforces flatness (`"additionalProperties": false`, no nested objects except `label_fields`).

### Sources
[pg_jsonschema](https://supabase.com/docs/guides/database/extensions/pg_jsonschema) · [Managing JSON](https://supabase.com/docs/guides/database/json)

### Verify later
- Exact statutory thresholds per target jurisdiction (CH HyV Anhang; AT LMSVG; DE LMHV; US FDA Food Code 2022) — legal sources, unblocked network needed.

---

## 4. i18n architecture

### Recommendation
- **Source locale: `de-CH`** (ß-free, «guillemets», `Fr.`/`CHF`). Every key is authored in de-CH first; `de-DE`, `de-AT` are *overlays* containing only keys that differ (ß, «Jause», currency), resolved by fallback chain `de-AT → de-CH → en`.
- **One JSON file per locale**, `app/i18n/de-CH.json`, `fr-CH.json`, `it-CH.json`, `en.json`, loaded on demand with `fetch()` and cached by the service worker (§5). Keys are namespaced (`board.reserve`, `check.q1`, `protocol.temp_label`); values may contain ICU-lite placeholders `{count}` and plural blocks handled in ~40 lines of vanilla JS:

```js
const pr = new Intl.PluralRules(locale);
function t(key, vars = {}) {
  let s = dict[key] ?? fallback[key] ?? key;
  if (typeof s === 'object') s = s[pr.select(vars.count)] ?? s.other;   // {"one":"{count} Portion","other":"{count} Portionen"}
  return s.replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? '');
}
const fmtDT   = new Intl.DateTimeFormat(locale, { timeZone: city.timezone, dateStyle: 'short', timeStyle: 'short' });
const fmtRel  = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });   // "in 2 Std."
const fmtNum  = new Intl.NumberFormat(locale, { style: 'unit', unit: 'celsius' });
```

  `Intl.PluralRules`, `DateTimeFormat`, `RelativeTimeFormat`, `NumberFormat` (unit style) and `ListFormat` are available in all evergreen browsers and iOS Safari; no library needed. **[experience, verify]** exact minimum iOS version for `RelativeTimeFormat` (Safari 14).
- **Time zones come from `cities.timezone`**, never from the device: a Vienna moderator looking at Bern must see Bern's pickup window. All DB timestamps are `timestamptz`; formatting is the only place a zone appears.
- **Locale-bearing data in DB:** `allergen_lists.items[].labels` and `cities.name_i18n` are jsonb maps keyed by BCP-47; the client picks `labels[locale] ?? labels[base] ?? labels['de-CH']`. User-generated text (dish names, notes) is not translated — it is shown as typed, with the offer's `lang` tag for `lang=` attributes.
- **Translation workflow:** `scripts/i18n_extract.py` scans `app/**/*.js` for `t('…')` and `data-i18n` and fails CI if a key is missing in `de-CH.json`; missing keys in other locales are listed, not fatal, until release. Machine translation: an Edge Function `translate` (Claude via the existing proxy pattern, or DeepL) writes candidates into `translations_review(key, locale, mt_text, status)`; a reviewer accepts in a tiny admin view; accepted rows are exported back into the JSON files by script and committed — **the repo, not the DB, is the source of truth for UI strings** (DB holds only per-city overrides such as the city's own greeting).
- **Coverage meter** runs in pre-commit (lesson from Sautero: a meter that only runs at session close protects nothing).
- **RTL readiness now, cheaply:** `<html lang dir>` set at boot from locale; CSS uses logical properties only (`margin-inline-start`, `padding-inline`, `inset-inline-end`, `text-align: start`); no `left/right` in the stylesheet (a lint grep). Icons that imply direction (arrows) get `[dir=rtl] & { transform: scaleX(-1) }`. Nothing else is needed until an RTL locale is actually planned.

### Trade-offs
- Hand-rolled ICU subset vs. a library (i18next, FormatJS): the subset covers plural + placeholders, which is 100 % of current strings. Ordinal/select/nested plural would justify FormatJS later; keep the JSON shape FormatJS-compatible (`{count, plural, one {…} other {…}}` can be generated from our object form) so the swap is a build step, not a rewrite.
- Lazy-loading dictionaries adds one request on first run; the service worker precaches the default locale of the city.

### Sources
No Supabase doc applies; browser-platform knowledge **[experience, verify]** for Safari/iOS minimums.

---

## 5. Frontend architecture

### Recommendation
**Stay buildless. Leave the single file. Move to ES modules with an import map.**

```html
<script type="importmap">
{ "imports": {
  "@supabase/supabase-js": "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.86.0/+esm",
  "app/": "./js/" } }
</script>
<script type="module" src="./js/main.js"></script>
```

- Module layout: `js/main.js` (boot, router), `js/sb.js` (client, session), `js/i18n.js`, `js/config.js` (bootstrap payload), `js/views/{board,mine,offer,protocol,admin}.js`, `js/lib/{dom,fmt,geo}.js`, `js/sw-register.js`. No bundler, no TypeScript — but **JSDoc + `// @ts-check` + `tsc --noEmit` in CI** using types generated by `supabase gen types --lang typescript` gives compile-time column checking for free ([Generating types](https://supabase.com/docs/guides/api/rest/generating-types)). Rule 9 ("never write a name you have not read") becomes machine-enforced.
- Pin the supabase-js version and add `integrity=` SRI on the CDN import; or vendor the ESM build into `app/vendor/` to remove the CDN from the trust chain and the network-call check in the deploy workflow. **[experience]** vendoring is preferable for a PWA that must work offline.
- **PWA:** `manifest.webmanifest` (per-city `name`/`theme_color` served via a tiny Edge Function or generated per city at build time — see §9), service worker with three strategies: precache app shell + default dictionary; network-first with cache fallback for `app_bootstrap`; **never cache authenticated data API responses** (RLS-scoped, per-user). Offline *reads* = last board snapshot in IndexedDB rendered with an "offline since 12:03" banner. Offline *writes* = only `handover_events` (the protocol is filled in cellars and loading bays): queue to IndexedDB, replay via Background Sync where available, else on next `online` event; events carry a client-generated `client_event_id uuid` unique index for idempotent replay.
- **Realtime → notifications, two tiers:**
  1. *In-app live list* (page open): replace the unfiltered `postgres_changes` with **Broadcast from the database** — a trigger on `offers` calls `realtime.broadcast_changes('city:' || new.city_id, …)`; clients join `city:<id>` as a **private** channel; authorisation is one RLS policy on `realtime.messages` checking `realtime.topic()` against the user's cities. This is the docs' recommended method "for scalability and security", because Postgres Changes runs one RLS read per subscriber per change and is single-threaded ([Subscribing to changes](https://supabase.com/docs/guides/realtime/subscribing-to-database-changes), [Postgres Changes → Limitations](https://supabase.com/docs/guides/realtime/postgres-changes), [Realtime authorization](https://supabase.com/docs/guides/realtime/authorization)). Broadcast Authorization is "public beta" ([Features](https://supabase.com/docs/guides/getting-started/features)); messages are stored in `realtime.messages` for 3 days and replayable (`replay.since`, max 25) — enough to catch up after a reconnect ([Broadcast](https://supabase.com/docs/guides/realtime/broadcast)). Free quota: 2 M messages, 200 peak connections; Pro 5 M / 500 ([Realtime pricing](https://supabase.com/docs/guides/realtime/pricing)).
  2. *Page closed* (the real need for takers): **Web Push** via an Edge Function. `push_subscriptions(user_id, org_id, city_id, endpoint, p256dh, auth, ua, created_at)` with RLS `user_id = (select auth.uid())`; a Database Webhook on `offers` INSERT (a `pg_net` trigger, asynchronous) calls `functions/v1/notify-offer`, which selects subscribers in the same `city_id` with `kind in ('taker','both')`, filters by the org's preferences (veg/hot/pork radius), sends VAPID-signed pushes, deletes 404/410 endpoints ([Database webhooks](https://supabase.com/docs/guides/database/webhooks), [pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)). VAPID private key in Edge Function secrets. Edge Function limits: 256 MB, 2 s CPU, 150 s wall on Free / 400 s paid, ports 25/587 blocked ([Limits](https://supabase.com/docs/guides/functions/limits)) — fan-out of a few hundred pushes fits; beyond that, queue (§6).
- **Install prompt:** capture `beforeinstallprompt`, show a "Zum Home-Bildschirm" card after the second visit; on iOS show the Share → Add-to-Home-Screen hint, because **Web Push on iOS works only for installed Home-Screen web apps (iOS 16.4+)** **[experience, verify current status]**.
- **When to adopt a framework:** never for this scope, unless (a) more than one regular front-end developer, or (b) a view needs > ~15 interdependent reactive states (e.g. a live dispatch map). Then Lit or Preact+HTM via import map — still no bundler. React/Tailwind is explicitly out (project rule).
- **Testing:**
  - RLS/pgTAP: `supabase test db` on every PR against `supabase start` in GitHub Actions; every policy gets a positive and a negative test; tests set `set local role authenticated; set local request.jwt.claims …` ([Testing overview](https://supabase.com/docs/guides/local-development/testing/overview), [Testing your database](https://supabase.com/docs/guides/database/testing)). Migrations move into `supabase/migrations/` so `db reset` replays them ([CLI workflows](https://supabase.com/docs/guides/local-development/cli-workflows)).
  - E2E: Playwright against the local stack (Free) — Inbucket/Mailpit captures magic links locally; on Pro, against a preview branch created per PR, which has its own DB, auth, storage and functions ([Working with branches](https://supabase.com/docs/guides/deployment/branching/working-with-branches)). Branching is "beta" and Pro-only ([Production checklist → Deployment](https://supabase.com/docs/guides/deployment/going-into-prod)).
  - Contract: a JS test that loads `app_bootstrap` JSON and asserts the Freigabe-Check renders N questions from the ruleset (guards against hard-coding creeping back).

### Trade-offs
- Import maps need Safari ≥ 16.4 / Chrome ≥ 89 — acceptable for a 2027 launch; a fallback `<script nomodule>` message suffices.
- Web Push adds a subscription table with endpoints that are personal data (§10 retention: delete after 90 days without a successful delivery).
- Broadcast-from-DB requires `private: true` channels and Realtime Authorization; misconfiguring the public/private flag silently drops messages (docs note both sides must match).

### Sources
[Broadcast](https://supabase.com/docs/guides/realtime/broadcast) · [Subscribing to database changes](https://supabase.com/docs/guides/realtime/subscribing-to-database-changes) · [Postgres Changes](https://supabase.com/docs/guides/realtime/postgres-changes) · [Realtime authorization](https://supabase.com/docs/guides/realtime/authorization) · [Realtime pricing](https://supabase.com/docs/guides/realtime/pricing) · [Database webhooks](https://supabase.com/docs/guides/database/webhooks) · [pg_net](https://supabase.com/docs/guides/database/extensions/pg_net) · [Edge Function limits](https://supabase.com/docs/guides/functions/limits) · [Testing overview](https://supabase.com/docs/guides/local-development/testing/overview) · [Working with branches](https://supabase.com/docs/guides/deployment/branching/working-with-branches) · [Generating types](https://supabase.com/docs/guides/api/rest/generating-types)

### Verify later
- iOS Web Push for installed PWAs: current Safari version constraints, badge/actions support.
- Realtime per-plan limits page (`/docs/guides/realtime/limits`) for channels-per-client and message size — the search returned it by reference only.

---

## 6. Backend / platform

### Recommendation
**One project for Switzerland now; one project per *legal region* later (EU/EEA can share; a non-adequate country gets its own).** Decide the *region* of the CH project before Pro, because a project cannot change region in place (**[experience, verify]** — docs describe "Restore to a new project"/duplicate, not in-place region moves).

- **Region:** Paris (`eu-west-3`) is inside the EU. For Swiss revDSG, transfers to the EU are to countries with adequate protection (FDPIC list) **[experience, verify]**, so Paris is legally fine for a Bern pilot. Supabase also offers **Zurich (`eu-central-2`)** — the GDPR page lists it in the "Europe" grouping and warns it is *not* EU ([GDPR compliance](https://supabase.com/docs/guides/security/gdpr-compliance)); the PrivateLink page confirms the region code ([PrivateLink](https://supabase.com/docs/guides/platform/privatelink)). For a municipality-facing product, "Daten in der Schweiz" is a sales argument; for later EU cities Paris is the safer default. Proposal: **create the Pro project in Zurich when going live in Bern** (migrate data via `db dump`/restore while the dataset is tiny), keep Paris as the staging project. If a second *EU* country comes, either serve it from Zurich (adequacy decision for CH exists) or open a Frankfurt/Paris project — the schema and app are region-agnostic by §1 (`config.js` per deployment).
  Caveat: Edge Functions regional invocation list has **no Zurich** ([Regional invocations](https://supabase.com/docs/guides/functions/regional-invocation)) — functions run "closest to the user" by default, which is fine for notifications; DB-heavy functions would pay a Zurich↔Frankfurt hop.
- **When Pro becomes necessary — the day the first non-team user must receive a magic link.** The default SMTP "will refuse to deliver messages to addresses that are not part of the project's team" and is rate-limited "not meant for production" ([Custom SMTP](https://supabase.com/docs/guides/auth/auth-smtp)). Custom SMTP (Resend/Postmark/SES) removes that; after enabling, the default is a low 30 emails/hour until raised in Rate Limits ([Custom SMTP](https://supabase.com/docs/guides/auth/auth-smtp), [Production checklist](https://supabase.com/docs/guides/deployment/going-into-prod)). Whether custom SMTP is configurable on Free is not stated in the pages retrieved — **[verify]**; regardless, Free pauses after 7 idle days, which a pilot cannot tolerate, and Free has no downloadable backups ([Production checklist](https://supabase.com/docs/guides/deployment/going-into-prod)). Pro: $25/mo + compute (Micro ≈ $10, covered by the $10 credit; Nano is billed as Micro on paid plans and cannot be newly launched there) ([Compute](https://supabase.com/docs/guides/platform/manage-your-usage/compute)); 7 days of daily backups ([Backups](https://supabase.com/docs/guides/platform/backups)). PITR (7-day ≈ $100/mo, needs ≥ Small compute) is **not** needed for the pilot; the docs recommend it above 4 GB or when RPO < 24 h matters ([Backups](https://supabase.com/docs/guides/platform/backups), [Production checklist](https://supabase.com/docs/guides/deployment/going-into-prod)).
- **Auth flow tweaks:** switch magic link to **email OTP code** for the kitchen phone flow (link-in-email breaks when the mail app opens a different browser than the installed PWA) — same `signInWithOtp`, template change only ([Passwordless](https://supabase.com/docs/guides/auth/auth-email-passwordless)). Use `shouldCreateUser: false` on the login form and a separate "join by invitation" path (§7). OTP validity ≤ 1 h per the checklist. Enable CAPTCHA on sign-up when abuse appears (docs list it as the most effective bot mitigation).
- **Scheduled work — all in Postgres, no external cron:**
  - `pg_cron` every 5 min: `update offers set status='expired' where status in ('open','reserved') and pickup_to < now()` **plus** emit an `expired` event; nightly: retention jobs (§10), materialised stats refresh (§9). Sub-minute schedules are supported; job names are immutable ([Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)).
  - `pg_cron` + `pg_net` + Vault to invoke Edge Functions on a schedule — the docs' exact recipe, secrets in Vault not in the job text ([Scheduling Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions), [Vault](https://supabase.com/docs/guides/database/vault)).
- **Outbound messaging via `pgmq`:** queue `outbound_messages` (durable "Basic" queue). Producers: DB triggers (`offer published` → notify takers; `reserved` → notify kitchen; `handover_complete` → send both parties a PDF link). Consumer: Edge Function `dispatch` invoked by `pg_cron` every minute (and immediately via `pg_net` for latency-critical events), which `pgmq.read(queue, vt=60, qty=50)` → sends via channel adapter (Resend e-mail, Web Push, Twilio SMS, WhatsApp Cloud API, Signal via `signal-cli` on a tiny VPS **[experience]**) → `pgmq.archive` on success, leaves for retry on failure; `read_ct > 5` → dead-letter queue. Do **not** expose `pgmq_public` to clients — queues stay server-side; the docs are explicit that pgmq tables have no RLS by default ([PGMQ](https://supabase.com/docs/guides/queues/pgmq), [Queues quickstart](https://supabase.com/docs/guides/queues/quickstart)).
  Prefer channel *preferences* over channel *sprawl*: e-mail + Web Push at launch; SMS only for the "your reservation was cancelled 20 min before pickup" class; WhatsApp only if the pilot takers already coordinate there (README says they do — but Business API template approval and costs must be checked).
- **Rate limiting:** Auth endpoints are covered by Supabase (OTP 360/h project-wide default, 60 s per user) ([Rate limits](https://supabase.com/docs/guides/auth/rate-limits)). Data API has no per-user limiter → enforce business limits in RPCs: `check_rate('publish_offer', 20, interval '1 hour')` against a `rate_events(user_id, action, at)` table (indexed, pruned by cron). Edge Functions: per-IP token bucket in a `kv`-style table or Upstash **[experience]**.
- **Abuse prevention:** approval gate stays (org `status='pending'` sees nothing; §1 policies include `org.status='approved'` via the helper); `reports(reporter_org, target_type, target_id, reason, created_at)` + moderator queue; `before-user-created` Auth Hook to block disposable-mail domains ([Before user created hook](https://supabase.com/docs/guides/auth/auth-hooks/before-user-created-hook)).

### Trade-offs
- Zurich vs Paris: Zurich wins on positioning, Paris on Edge-Function locality and EU expansion. Both work legally for CH. The cost of choosing wrong is one dump/restore while data is small — so decide before the first real protocol event is stored, not later.
- pgmq + Edge Function polling every minute = ~43 k invocations/month; Free includes 500 k, Pro 2 M ([Billing quotas](https://supabase.com/docs/guides/platform/billing-on-supabase)). Fine.
- Third-party channels are "your responsibility"; Supabase does not monitor them ([Shared responsibility](https://supabase.com/docs/guides/deployment/shared-responsibility-model)) — the dispatcher logs every attempt to `message_log` so §8 can alert on failure rate.

### Sources
[GDPR compliance](https://supabase.com/docs/guides/security/gdpr-compliance) · [PrivateLink (region list)](https://supabase.com/docs/guides/platform/privatelink) · [Regional invocations](https://supabase.com/docs/guides/functions/regional-invocation) · [Custom SMTP](https://supabase.com/docs/guides/auth/auth-smtp) · [Production checklist](https://supabase.com/docs/guides/deployment/going-into-prod) · [Rate limits](https://supabase.com/docs/guides/auth/rate-limits) · [Passwordless](https://supabase.com/docs/guides/auth/auth-email-passwordless) · [Project pausing](https://supabase.com/docs/guides/platform/free-project-pausing) · [Backups](https://supabase.com/docs/guides/platform/backups) · [Compute](https://supabase.com/docs/guides/platform/manage-your-usage/compute) · [Cron quickstart](https://supabase.com/docs/guides/cron/quickstart) · [Scheduling Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions) · [Vault](https://supabase.com/docs/guides/database/vault) · [PGMQ](https://supabase.com/docs/guides/queues/pgmq) · [Queues quickstart](https://supabase.com/docs/guides/queues/quickstart) · [Before user created hook](https://supabase.com/docs/guides/auth/auth-hooks/before-user-created-hook) · [Shared responsibility](https://supabase.com/docs/guides/deployment/shared-responsibility-model)

### Verify later
- Regions page for the full current list and whether Zurich has any feature gaps (branching, read replicas).
- Custom SMTP availability on the Free plan.
- Resend/Postmark EU data-residency options; Twilio CH sender IDs; WhatsApp Business API template approval lead time and per-conversation pricing; Signal has no official business API.

---

## 7. Identity & access

### Recommendation
- **Roles live in tables, not in the JWT** — with one exception. `memberships.role` (`owner|staff`) and `city_roles.role` (`moderator|platform_admin`) are read by the `private.*` helpers on every request, so a removed member loses access on the next query, not on the next token refresh. The docs warn that `auth.jwt()` claims are "not always fresh" ([RLS guide → auth.jwt()](https://supabase.com/docs/guides/database/postgres/row-level-security)). The exception: a **Custom Access Token Hook** adds `app_metadata.platform_admin: true` for the handful of platform admins, so the client can render the admin UI without a round-trip; RLS still re-checks the table ([Custom claims & RBAC](https://supabase.com/docs/guides/api/custom-claims-and-role-based-access-control-rbac), [Custom access token hook](https://supabase.com/docs/guides/auth/auth-hooks/custom-access-token-hook)). Never read `user_metadata` in a policy (user-writable).
- **Permission matrix (pgTAP asserts every cell):**

| Action | staff | owner | city moderator | platform admin |
|---|---|---|---|---|
| publish/cancel offer for own org's sites | ✓ | ✓ | – | – |
| reserve as taker org | ✓ | ✓ | – | – |
| write handover events for own side | ✓ | ✓ | – | – |
| manage sites, invite/remove members | – | ✓ | – | – |
| approve/block orgs in city | – | – | ✓ | ✓ |
| see protocols of any org in city | – | – | ✓ (read) | ✓ |
| edit rulesets, cities, themes | – | – | – | ✓ |

- **Invite flow:** owner creates `invitations(id, org_id, email_hash, role, token_hash, expires_at, accepted_by)`; the dispatcher (§6) mails a link `?invite=<token>`; the invitee signs in (OTP, `shouldCreateUser: true` only when a valid invite token is present — checked by RPC `accept_invitation(token)` after sign-in, which compares `sha256(token)` and the session e-mail, inserts the membership, marks accepted). Tokens are one-time and 7-day. Uninvited sign-ups land in an org-less state and can only "create a new organisation" (→ pending approval).
- **Approval workflow:** `organisations.status` transitions `pending → approved | blocked` by a city moderator via RPC `set_org_status`, which writes `audit_log` and enqueues an e-mail. The Freigaben screen already exists; it becomes city-scoped.
- **Org verification (CH):** field `legal_id` = UID `CHE-###.###.###`; client-side checksum (mod-11) **[experience, verify algorithm]**; Edge Function `verify-uid` calls the Zefix public API (search by UID → legal name, seat, status) and stores `legal_id_verified_at`, `zefix_name`; moderator sees "Zefix: Restaurant X GmbH, Bern, aktiv" next to the self-declared name. Later countries: AT Firmenbuch, DE Handelsregister, FR SIRENE — same table, `legal_id_source` differs. NGOs without UID: manual verification + document upload to the private bucket.
- **SSO for municipalities (later):** SAML 2.0 is Pro+ and multi-tenant via `sso_provider_id` in the JWT; map `organisations.sso_provider_id` and use a *restrictive* policy so SSO users can only act inside their org ([SSO SAML](https://supabase.com/docs/guides/auth/enterprise-sso/auth-sso-saml)). Priced at $0.015 per SSO MAU above quota ([Billing](https://supabase.com/docs/guides/platform/billing-on-supabase)). Not before a municipality asks.
- **MFA:** TOTP enrollment offered to owners and required (restrictive `aal2` policy) for `city_roles` — moderators can see PII across orgs ([MFA](https://supabase.com/docs/guides/auth/auth-mfa)).

### Trade-offs
- Table-based roles cost one helper call per request (cached per statement); JWT roles are faster but stale. For a food-safety app where "removed staff must not see pickup addresses" matters, staleness loses.
- Zefix API is a hard external dependency; verification is asynchronous and never blocks approval — the moderator approves with or without it.

### Sources
[Custom claims & RBAC](https://supabase.com/docs/guides/api/custom-claims-and-role-based-access-control-rbac) · [Custom access token hook](https://supabase.com/docs/guides/auth/auth-hooks/custom-access-token-hook) · [SSO SAML](https://supabase.com/docs/guides/auth/enterprise-sso/auth-sso-saml) · [MFA](https://supabase.com/docs/guides/auth/auth-mfa) · [RLS guide](https://supabase.com/docs/guides/database/postgres/row-level-security)

### Verify later
- Zefix REST API: endpoint, auth (registration/API key), terms of use, rate limits.
- UID checksum specification (eCH-0097).

---

## 8. Observability & ops

### Recommendation
- **Logs:** Supabase Logs Explorer (ClickHouse SQL since June 2026, `source` column per service; API/Postgres/Realtime logs) plus the MCP `query_logs` tool for the assistant ([Query logs with SQL](https://supabase.com/docs/guides/observability/advanced-log-filtering)). Enable `log_min_duration_statement = 500ms` and `auto_explain` for slow queries ([Postgres log config](https://supabase.com/docs/guides/database/postgres/postgres-log-config)). Check Security and Performance Advisors weekly (already available via MCP `get_advisors`).
- **App error tracking:** an `client_errors` table is *not* the answer (PII in stack traces, unbounded growth). Use GlitchTip (self-hosted, EU) or Sentry with EU data residency and `beforeSend` scrubbing of e-mail/phone/address; sample 100 % of errors, 0 % of performance traces **[experience]**. Edge Function errors go to Supabase function logs; the dispatcher additionally writes `message_log(status, channel, error_code)`.
- **Uptime:** an external monitor (UptimeRobot/Better Stack, EU) hits `GET /rest/v1/rpc/health` (anon-callable, returns `{db: ok, ruleset_version, city_count}`) every 5 min and the static app URL; alert to phone. Realtime health via the Realtime report page ([Realtime reports](https://supabase.com/docs/guides/realtime/reports)).
- **Backups:** Pro daily backups (7 days) are the floor. Add a **weekly off-site logical dump** via GitHub Actions cron: `supabase db dump --linked | age -r <pubkey>` → private bucket in *another* provider; storage objects are not part of DB backups ([Backups](https://supabase.com/docs/guides/platform/backups)), so also `supabase storage cp -r` for the `protocols` bucket (legal records). Restore drill once per quarter into a scratch project; the drill is a runbook, and the runbook has a date of last execution in `facts.json`.
- **Runbooks (one page each, in `docs/runbooks/`):** project paused (Free) / restore; magic-link mail not arriving (SMTP reputation, rate limits, link scanners — the docs describe the scanner problem and the redirect-page fix); Realtime silent (public/private flag mismatch, `setAuth()` missing); expired offers not expiring (cron job inactive — `cron.job.active`); dispatcher backlog (`pgmq.metrics`); rollback of a migration (branch delete/recreate, `db reset --linked` **only** on staging); key rotation (publishable key is public by design; rotate the *secret* key and Edge Function secrets); data-subject request (export/delete by `user_id`).
- **Incident comms:** status page (static, on the same GitHub Pages) + templated German notice (Sautero's `pilot-comms` pattern). Breach: revDSG requires notification to the FDPIC "as soon as possible" when high risk; keep the template ready **[experience, verify wording]**.
- **Cost model (estimates; USD list prices from docs, CHF ≈ 0.85 × USD — verify the pricing page):**

| Stage | Plan & add-ons | USD/mo (list) | ≈ CHF/mo |
|---|---|---|---|
| Bern pilot (Free) | Free, Nano, default SMTP for team only | 0 | 0 |
| Bern live | Pro 25 + Micro compute 10 − 10 credits + custom domain 10 + Resend free tier | ≈ 35 | ≈ 30 |
| 5 cities (~300 orgs, ~2 000 MAU) | Pro 25 + Small 15 − 10 + custom domain 10 + PITR-7d 100 (optional) + Resend paid ~20 | ≈ 60 (160 with PITR) | ≈ 50–135 |
| 50 cities, 2 countries (~3 000 orgs, ~20 000 MAU, 2 projects) | Pro/Team + Medium 60 + Micro staging 10 − 10 + 2 domains 20 + PITR-14d 200 + log drain 60 + egress overage + SMS/WhatsApp usage | ≈ 350–600 + messaging | ≈ 300–500 + messaging |

  Quota anchors from docs: MAU 50 k Free / 100 k Pro; egress 5 GB / 250 GB; DB 500 MB / 8 GB; Realtime 2 M msgs & 200 peak conns / 5 M & 500; Edge invocations 500 k / 2 M ([Billing](https://supabase.com/docs/guides/platform/billing-on-supabase)). Compute price table: Micro ≈ $10, Small ≈ $15, Medium ≈ $60, Large ≈ $111 ([Compute](https://supabase.com/docs/guides/platform/manage-your-usage/compute)); PITR 7/14/28 days ≈ $100/$200/$400 ([PITR usage](https://supabase.com/docs/guides/platform/manage-your-usage/point-in-time-recovery)); custom domain ≈ $10 ([Custom domain usage](https://supabase.com/docs/guides/platform/manage-your-usage/custom-domains)); log drain ≈ $60 + events ([Log drain usage](https://supabase.com/docs/guides/platform/manage-your-usage/log-drains)). Custom domain, PITR, log drains and compute are **not** covered by the Spend Cap.

### Sources
[Query logs with SQL](https://supabase.com/docs/guides/observability/advanced-log-filtering) · [Postgres log config](https://supabase.com/docs/guides/database/postgres/postgres-log-config) · [Realtime reports](https://supabase.com/docs/guides/realtime/reports) · [Backups](https://supabase.com/docs/guides/platform/backups) · [Billing](https://supabase.com/docs/guides/platform/billing-on-supabase) · [Compute](https://supabase.com/docs/guides/platform/manage-your-usage/compute) · [PITR usage](https://supabase.com/docs/guides/platform/manage-your-usage/point-in-time-recovery) · [Custom domain usage](https://supabase.com/docs/guides/platform/manage-your-usage/custom-domains) · [Log drain usage](https://supabase.com/docs/guides/platform/manage-your-usage/log-drains)

### Verify later
- Current pricing page (Team plan price, spend-cap behaviour, egress price per GB); FDPIC breach-notification wording.

---

## 9. Public API & integrations

### Recommendation
- **Read-only public stats per city:** materialised view `stats.city_daily (city_id, day, offers_published, portions_offered, portions_handed_over, orgs_active, co2e_kg_est)` refreshed nightly by `pg_cron`; exposed **only** through a versioned view `api_v1.city_stats` with `security_invoker = true` (views created by `postgres` bypass RLS otherwise — docs warn) and `grant select … to anon`. Add `api_v1` to the exposed schemas; never expose `public` aggregates that could de-anonymise a single kitchen (k-anonymity ≥ 5 orgs per bucket, enforced in the view). Endpoint = PostgREST: `GET /rest/v1/city_stats?city=eq.bern` with the publishable key — no Edge Function needed. Cache headers via a Cloudflare Worker in front if load appears **[experience]**.
- **Open data:** same view as CSV — PostgREST returns CSV with `Accept: text/csv`; document it as `https://api.uebrig.ch/rest/v1/city_stats?…` once a custom domain exists (custom domains keep API URLs portable across projects and are a paid add-on ([Custom domains](https://supabase.com/docs/guides/platform/custom-domains))). Licence CC0 like the rest of the repo.
- **CSV export for municipalities/funders (authenticated):** RPC `export_protocols(p_org uuid, p_from date, p_to date) returns text` (moderators: any org in their city; owners: own org), streaming PostgREST CSV. Large exports → Edge Function writing a file into the private bucket and returning a signed URL (1 h).
- **Webhooks for partner tools:** `webhook_endpoints(org_id|city_id, url, secret, events text[], active)`; the same `pgmq` outbox (§6) carries `webhook.deliver` messages; the dispatcher signs with Standard Webhooks headers (`webhook-id`, `webhook-timestamp`, `webhook-signature` HMAC-SHA256) — the same scheme Supabase uses for its own hooks — and retries with backoff; deliveries logged in `webhook_deliveries`. Events: `offer.published`, `offer.reserved`, `offer.handed_over`, `offer.cancelled`, `org.approved`. Payload contains ids and non-PII summary; partners fetch details with their own JWT.
- **Inbound partner integration (TGTG-like):** partner posts to Edge Function `partner/offers` with an API key stored hashed in `api_keys(org_id, key_hash, scopes)`; the function acts with the secret key **but** sets `request.jwt.claims` to impersonate the org's service user before inserting, so RLS and triggers still apply **[experience]**.
- **API versioning:** schema per major version (`api_v1`, `api_v2`), views only, no tables. Breaking change = new schema, old one kept ≥ 12 months. Edge Functions carry the version in the path (`/functions/v1/partner-v1-offers`).
- **White-label per city:** `cities.theme jsonb` = design tokens (`{"--brand":"#0A1A2F","--accent":"#34F7D7","--radius":"12px","logo":"cities/bern/logo.svg","name":"Übrig Bern"}`) returned by `app_bootstrap(slug)`; boot applies `document.documentElement.style.setProperty()` per token; logo from a **public** bucket `brand` (public buckets are CDN-cached and skip RLS on read ([Buckets](https://supabase.com/docs/guides/storage/buckets/fundamentals))). City resolution order: subdomain (`bern.uebrig.ch`) → `?city=` → user's default city → geolocation prompt. The manifest is served per city by a tiny Edge Function (`/functions/v1/manifest?city=bern`) so the installed PWA carries the city name and colour. Content the city may override: greeting, imprint contact, partner logos — stored in `cities.content_i18n jsonb`, sanitised as text, **never** as HTML (single `escapeHtml` boundary, no `innerHTML` with user data — project rule §11).

### Trade-offs
- PostGIS views for a "map of all sites" as open data would expose kitchen locations; publish only city-level aggregates and *taker* organisations that opt in (`sites.public_listing boolean`).
- Version-per-schema means duplicate view definitions for a year; acceptable, and declarative schema files make the diff obvious ([CLI workflows](https://supabase.com/docs/guides/local-development/cli-workflows)).

### Sources
[RLS guide → Views](https://supabase.com/docs/guides/database/postgres/row-level-security) · [Custom domains](https://supabase.com/docs/guides/platform/custom-domains) · [Buckets](https://supabase.com/docs/guides/storage/buckets/fundamentals) · [Working with branches (webhook payload uses Standard Webhooks)](https://supabase.com/docs/guides/deployment/branching/working-with-branches)

### Verify later
- PostgREST CSV output on the current Supabase PostgREST version; response size limits for `text/csv` via the Data API.

---

## 10. Security & compliance

### Recommendation

**RLS review checklist (run by `rls-guard` or by hand; each item = a pgTAP test where possible):**
1. Every table in an exposed schema has RLS enabled (event trigger `rls_auto_enable` from the docs installed so new tables cannot forget it) ([RLS guide](https://supabase.com/docs/guides/database/postgres/row-level-security)).
2. Every policy names `to authenticated` or `to anon`; none is `to public`.
3. Every `auth.uid()`/`auth.jwt()`/`private.*` call is wrapped in `(select …)`; Advisor lint 0003 is clean.
4. Every tenant column used in a policy is indexed.
5. No policy on table A subqueries table B under RLS — use a `private.` SECURITY DEFINER helper with `set search_path = ''`.
6. SECURITY DEFINER functions live in `private` (not exposed), have `EXECUTE` revoked from `anon`/`public`, and never take row data as a parameter that would defeat the initPlan cache.
7. `UPDATE` policies have both `USING` and `WITH CHECK`; `WITH CHECK` pins every column the client must not change (today's `offers_update_kitchen` fails this — §0).
8. Views are `security_invoker = true` or live in an unexposed schema.
9. Storage: private by default; every `storage.objects` policy pins `bucket_id`; listing vs. download separated with `storage.allow_only_operation('object.list')` where needed ([Storage helpers](https://supabase.com/docs/guides/storage/schema/helper-functions)).
10. Realtime: "Allow public access" off; `realtime.messages` policies check `realtime.topic()` against tenant membership ([Realtime authorization](https://supabase.com/docs/guides/realtime/authorization)).
11. `pgmq`, `net`, `vault`, `cron`, `private`, `stats` schemas are **not** in the exposed list; `vault.decrypted_secrets` has no grant to `authenticated`.
12. Negative tests: anon sees zero rows everywhere except `api_v1`; staff of org A cannot read org B; a removed member (status `removed`) loses access without token refresh; a pending org sees no open offers.
13. Generic guard: a pgTAP test that iterates `pg_policies` and fails on any policy whose `qual` contains `auth.uid()` not preceded by `(select`.

**Secrets:** the publishable key in `config.js` is public by design; it grants nothing beyond RLS ([RLS guide → Bypassing](https://supabase.com/docs/guides/database/postgres/row-level-security)). The secret key exists only in Edge Function secrets and GitHub Actions secrets; third-party API keys (Resend, Twilio, VAPID, Zefix) in Edge Function secrets; keys needed *inside* SQL (cron → function auth) in Vault ([Vault](https://supabase.com/docs/guides/database/vault)). Enable SSL enforcement and Network Restrictions on the DB; MFA on the Supabase org with two owners ([Production checklist](https://supabase.com/docs/guides/deployment/going-into-prod)).

**PII minimisation:**
- Phone numbers: move to `contact_channels(org_id, kind, value, visible_after text)` and reveal only to the counterparty of a *reserved* offer (today's `profiles_select_counterpart` reveals the kitchen's phone to every approved taker for every open offer — tighten to reserved-only, kitchens' pickup address stays visible since it *is* the offer).
- Person names: the protocol needs "who handed over" — store `actor_id`; render the name from `profiles` at read time; after retention, the join returns "ehemaliges Mitglied".
- Push endpoints, IP addresses in `audit_log`: 90-day retention.
- Photos of dishes: optional, no faces, EXIF stripped client-side **[experience]**.

**Retention (pg_cron nightly, each step idempotent and logged):**
- `offers`: 30 days after `pickup_to` → `note`, `address` copy nulled (site remains), status kept; 24 months → row deleted, aggregate already in `stats.city_daily`.
- `handover_events`: payload PII (`signature_ref`, free text) removed after **24 months**; temperatures/times/counts kept for the statutory self-control retention — CH practice is commonly cited as 2 years **[experience, verify with cantonal lab]**; the row itself is never deleted (hash chain).
- `invitations` 30 days after expiry; `rate_events` 7 days; `message_log` 90 days; `auth.users` without membership and without login for 12 months → deleted via admin API (their events keep `actor_id` as a dangling UUID, which is the point).

**revDSG (CH, in force 1.9.2023):** privacy notice at first sign-in (what, why, retention, Supabase as processor in FR/CH, Resend/Twilio as sub-processors, rights, FDPIC); a **processing register** (Verzeichnis der Bearbeitungstätigkeiten) — not mandatory below 250 employees unless high-risk, but a one-page register is cheap and funders ask; **DPA with Supabase** — Supabase provides one on request ([GDPR compliance → DPA](https://supabase.com/docs/guides/security/gdpr-compliance)); Supabase is SOC 2 Type 2 ([Security](https://supabase.com/docs/guides/security)). Health data is not processed (allergens describe food, not people — keep it that way; never store a taker's allergies).

**EU expansion notes:** GDPR Art. 28 processor contract = the same Supabase DPA; data location Paris (EU) or Zurich (adequate third country, per the docs' own note that Zurich is not EU and needs a specific EU region if EU-only is required) ([GDPR compliance](https://supabase.com/docs/guides/security/gdpr-compliance)); Art. 30 register becomes mandatory-in-practice; Art. 33 72-hour breach notice; cookie/consent: the app sets only functional storage (session, locale) — no consent banner needed, but state it in the notice **[experience, verify per country]**.

### Sources
[RLS guide](https://supabase.com/docs/guides/database/postgres/row-level-security) · [Storage helpers](https://supabase.com/docs/guides/storage/schema/helper-functions) · [Realtime authorization](https://supabase.com/docs/guides/realtime/authorization) · [Vault](https://supabase.com/docs/guides/database/vault) · [Production checklist](https://supabase.com/docs/guides/deployment/going-into-prod) · [GDPR compliance](https://supabase.com/docs/guides/security/gdpr-compliance) · [Security overview](https://supabase.com/docs/guides/security)

### Verify later
- Statutory retention for food-safety self-control records in CH (HyV) and AT; FDPIC guidance on processing registers for small entities; Supabase DPA text and sub-processor list.

---

## 11. Phased build plan

Conventions for every phase: migrations are numbered files in `db/` **and** mirrored to `supabase/migrations/` so `supabase db reset` replays them; every migration ships with `supabase/tests/database/NNN_*.test.sql` (pgTAP); "rollback" = the forward migration that undoes it, written *before* the change ships; nothing is "done" until seen on a real phone against the live project.

### Phase 0 — now: Bern pilot, nothing that breaks
- **Migrations:** `002_hardening.sql` (additive/compatible only): wrap helper calls in `(select …)`; pin `status` in `offers_update_kitchen` `WITH CHECK` (`status in ('open','cancelled')`); replace `profiles_select_counterpart`'s correlated subquery with `private.can_see_profile(uuid)`; add `cities` table with one row `bern` and `offers.city_id` default → Bern (nullable, trigger-filled); remove `profiles` from the realtime publication.
- **RLS tests:** pgTAP: taker cannot set `picked` via UPDATE; taker sees kitchen phone only for open/reserved-by-me offers; anon sees nothing.
- **App:** none required; optional: switch to OTP code template; add `shouldCreateUser` handling.
- **Ops:** custom SMTP (Resend) + Pro **if** any non-team user must log in; otherwise keep Free and a weekly `db dump` in CI; decide Zurich vs Paris (§6).
- **Rollback:** `002_down.sql` drops the new policies and re-creates the old ones (kept verbatim in the file).
- **Exit:** Advisor security/performance lints clean; pgTAP green in CI; one real kitchen and one real taker completed a reservation on their phones.

### Phase 1 — org/membership + cities + rulesets, dual-write, feature flags
- **Migrations:** `003_orgs.sql` (tables from §2 minus events; backfill; `offers_fill_tenant` trigger; new org policies alongside old); `004_rulesets.sql` (rulesets, allergen_lists, seed CH + EU14, `active_ruleset`, `app_bootstrap`); `005_drop_legacy_policies.sql` after two weeks of both running.
- **RLS tests:** matrix from §7 (every cell); dual-shape equivalence test (legacy insert with only `kitchen_id` yields identical visibility to new-shape insert); ruleset resolver returns CH values for Bern at three dates.
- **App:** ES-module split behind the same URL (Phase 1a, no behaviour change); read thresholds/allergens from `app_bootstrap`; org switcher and site picker behind `features.orgs_ui`; i18n moved to JSON files + `t()` with plurals.
- **Rollback:** feature flag off restores the old UI instantly; `003_down.sql` drops the new tables (data loss only of orgs created after backfill — acceptable in a flag-off scenario); never drop legacy columns in this phase.
- **Exit:** every Bern profile has an org, a membership and (kitchens) a geocoded site; zero hard-coded thresholds in `app/` (grep guard in pre-commit for `65`, `72`, `1,2,3,4,5,6,7,8,9,10,11,12,13,14`); i18n coverage 100 % de-CH, ≥ 95 % fr/en.

### Phase 2 — protocol event log + notifications + PWA
- **Migrations:** `006_events.sql` (handover_events, immutability, hash chain, jsonb schemas, RPCs rewritten to emit events, `offers.status` derived); `007_storage.sql` (private `protocols` bucket + policies, public `brand`); `008_queue.sql` (`pgmq` queue, `push_subscriptions`, `message_log`, cron jobs: expiry, dispatcher, retention); `009_realtime.sql` (broadcast trigger on offers, `realtime.messages` policy, publication emptied).
- **Edge Functions:** `dispatch`, `notify-offer` (or folded into dispatch), `manifest`.
- **RLS tests:** events immutable (UPDATE/DELETE raise); taker org reads only its own offers' events; storage policy positive/negative; realtime policy: user in Bern cannot join `city:zuerich`; queue schemas not exposed (test `information_schema` grants).
- **App:** protocol screen driven by ruleset (`require_temp_at_handover`), offline queue with idempotent replay, service worker, install prompt, Web Push opt-in, broadcast channel replaces `postgres_changes`.
- **Rollback:** Postgres Changes kept subscribable for one release (both paths coded); dispatcher can be paused via `cron.alter_job(active := false)`; events table stays (append-only, harmless).
- **Exit:** a full handover with temperature + both-party confirmation exported as CSV/PDF and shown to the Bern pilot's food inspector contact; push notification received on an installed iOS PWA and on Android; Realtime peak connections and message counts observed in the report page under Free/Pro quota.

### Phase 3 — second city, white-label, public stats
- **Migrations:** `010_city2.sql` (insert city row, theme, moderators; **no schema change** — that is the test); `011_stats.sql` (`stats` schema, materialised views, `api_v1` views with `security_invoker`, anon grants); `012_webhooks.sql` (endpoints, deliveries).
- **RLS tests:** a Zürich moderator cannot approve a Bern org; `api_v1.city_stats` never returns a bucket with < 5 orgs; anon can read `api_v1` only.
- **App:** city resolution (subdomain → param → default), theme tokens at boot, per-city manifest; public stats page (static, fetches `api_v1`).
- **Ops:** Pro, custom domain `api.uebrig.ch`, PITR decision, preview branches for PRs, uptime monitor, restore drill #1.
- **Rollback:** `cities.status = 'closed'` hides a city everywhere (policies include `city.status <> 'closed'`); views can be dropped without touching tables.
- **Exit:** second city onboarded by a moderator through the UI with **zero commits**; stats endpoint documented and consumed by at least one external party (municipality dashboard or journalist).

### Phase 4 — second country: rulesets, locale, project/region decision
- **Migrations:** `013_country.sql` (rulesets `scope='country'` for AT/DE, `allergen_lists` unchanged for EU, `cities` rows with `country`, `de-AT` overlay file); `014_legal_ids.sql` (`legal_id_source` values, verification function per country).
- **Decision:** same project (Zurich/Paris) vs. new project per legal region — driven by (a) the target country's transfer rules toward the current region, (b) a municipal contract demanding in-country hosting, (c) latency. If a new project: `supabase db dump --schema-only` + migrations replay + seed rulesets; the app is pointed at it by `config.js` per deployment; cross-project stats via the `api_v1` endpoints, not DB links.
- **RLS tests:** an AT moderator sees no CH data even with the same schema; ruleset resolver picks AT values for Vienna; de-AT overlay resolves to de-CH for missing keys.
- **Exit:** Vienna pilot offer published with AT rules and AT date/currency formatting, no code fork; legal review of the AT privacy notice done; DPA/Art. 28 covered.

### Things to verify with unblocked network
1. **Supabase pricing page** — Pro/Team fees, spend cap, egress per GB, current compute table; and **regions page** — full list incl. `eu-central-2` Zurich and any feature gaps.
2. **Realtime limits page** (`/docs/guides/realtime/limits`) — channels per connection, message size, joins/sec per plan.
3. **Custom SMTP on Free plan** — allowed or Pro-only.
4. **Web Push on iOS PWA** — minimum iOS/Safari version, requirement to be installed to Home Screen, support for actions/badges (2026 state).
5. **Zefix API** — public REST endpoint, registration, terms, quotas; **UID checksum** spec (eCH-0097).
6. **WhatsApp Business (Cloud API) terms** — template approval, per-conversation pricing in CH/AT, opt-in wording; Twilio CH alphanumeric sender rules; Signal (no official API — confirm).
7. **revDSG** specifics: FDPIC adequacy list (EU listed), breach-notification duty wording, processing-register threshold; **CH HyV** retention period for self-control records; AT LMSVG equivalents.
8. **Supabase DPA** text and sub-processor list (needed for the privacy notice).
9. **PostgREST CSV** support and size limits on the current Supabase version.
10. **Import maps / `Intl.RelativeTimeFormat`** minimum Safari versions for the pilot's phones.
11. Postgres **log retention per plan** (for the pgaudit decision).
12. Whether **project region can be changed** without a new project (docs seen only describe restore/duplicate).

---

### Scope declined
- **Schema-per-tenant or project-per-city:** rejected in §1 — cost, cross-tenant users, and no Supabase doc support for the pattern.
- **A framework or bundler now:** rejected in §5 — one developer, ~10 views; ES modules + import map + `tsc --noEmit` on JSDoc give the maintainability without a build step.
- **Storing UI translations in the database:** rejected in §4 — repo is the source of truth; only per-city content overrides live in `cities`.
- **PITR, log drains, read replicas for the pilot:** deferred to Phase 3/4 with explicit triggers (DB > 4 GB, regulator/funder demand, second region).
- **Storing takers' personal allergies or any health data:** declined permanently in §10 — the product needs allergens *of food*, not of people.
- **Exposing `pgmq_public` to browsers:** declined in §6 — queues stay server-side.
