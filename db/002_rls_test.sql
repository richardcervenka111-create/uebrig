-- Übrig Bern: RLS-Selbsttest zu 002_hardening.sql (25.09.2026). Als Migration ausführen, Ergebnis lesen:
--   select n, test from public.rls_test_002 order by n;   danach: drop table public.rls_test_002;
-- Legt drei Testbenutzer + zwei Angebote an, spielt Client-Rollen per set local role / request.jwt.claims,
-- sammelt Ergebnisse und löscht die Testdaten wieder. Erwartungswerte stehen im Text jedes Tests.
create table if not exists public.rls_test_002(n int, test text);
do $$
declare
  k uuid := '11111111-1111-1111-1111-000000000001';
  t uuid := '11111111-1111-1111-1111-000000000002';
  u uuid := '11111111-1111-1111-1111-000000000003';
  o1 uuid; o2 uuid; r text[] := '{}'; c int; rec public.offers;
begin
  insert into auth.users (id, instance_id, aud, role, email, encrypted_password, email_confirmed_at, created_at, updated_at, raw_app_meta_data, raw_user_meta_data, is_sso_user)
  values (k,'00000000-0000-0000-0000-000000000000','authenticated','authenticated','rls002-k@test.local','',now(),now(),now(),'{"provider":"email","providers":["email"]}','{}',false),
         (t,'00000000-0000-0000-0000-000000000000','authenticated','authenticated','rls002-t@test.local','',now(),now(),now(),'{"provider":"email","providers":["email"]}','{}',false),
         (u,'00000000-0000-0000-0000-000000000000','authenticated','authenticated','rls002-u@test.local','',now(),now(),now(),'{"provider":"email","providers":["email"]}','{}',false);
  insert into public.profiles (id, role, org, contact, phone, address, approved, lang) values
   (k,'kitchen','Testküche','Kim Koch','031 000 00 01','Teststrasse 1', true,'de'),
   (t,'taker','Testabnehmer','Tom Taker','031 000 00 02',null,true,'de'),
   (u,'taker','Unfrei','Uli Unfrei','031 000 00 03',null,false,'de');
  insert into public.offers (kitchen_id,dish,portions,made_at,use_by,pickup_from,pickup_to,address,check_ok)
   values (k,'Testgericht eins',5,now()-interval '1 hour',now()+interval '20 hours',now(),now()+interval '2 hours','Teststrasse 1',true) returning id into o1;
  insert into public.offers (kitchen_id,dish,portions,made_at,use_by,pickup_from,pickup_to,address,check_ok)
   values (k,'Testgericht zwei',6,now()-interval '1 hour',now()+interval '20 hours',now(),now()+interval '2 hours','Teststrasse 1',true) returning id into o2;

  perform set_config('request.jwt.claims', json_build_object('sub',t,'role','authenticated')::text, true);
  execute 'set local role authenticated';
  select count(*) into c from public.profiles; r := r || ('T sieht Profile (erwartet 2 = eigenes + Küche): '||c);
  select count(*) into c from public.offers; r := r || ('T sieht offene Angebote (erwartet 2): '||c);
  begin update public.offers set status='picked' where id=o1; get diagnostics c = row_count; r := r || ('T setzt picked direkt: '||c||' Zeilen (erwartet 0)');
  exception when others then r := r || ('T setzt picked direkt: blockiert – '||sqlerrm); end;
  execute 'reset role';

  perform set_config('request.jwt.claims', json_build_object('sub',k,'role','authenticated')::text, true);
  execute 'set local role authenticated';
  begin update public.offers set status='picked' where id=o1; get diagnostics c=row_count; r := r||('K setzt picked direkt: '||c||' Zeilen (erwartet blockiert)');
  exception when others then r := r||('K setzt picked direkt: blockiert – '||sqlerrm); end;
  begin update public.offers set status='expired' where id=o1; get diagnostics c=row_count; r := r||('K setzt expired direkt: '||c||' Zeilen (erwartet blockiert)');
  exception when others then r := r||('K setzt expired direkt: blockiert – '||sqlerrm); end;
  begin update public.offers set reserved_by=t where id=o1; get diagnostics c=row_count; r:=r||('K setzt reserved_by direkt: '||c||' Zeilen (erwartet blockiert)');
  exception when others then r:=r||('K setzt reserved_by direkt: blockiert – '||sqlerrm); end;
  begin update public.offers set kitchen_id=t where id=o1; get diagnostics c=row_count; r:=r||('K verschiebt Angebot zu fremder Küche: '||c||' Zeilen (erwartet blockiert)');
  exception when others then r:=r||('K verschiebt Angebot zu fremder Küche: blockiert – '||sqlerrm); end;
  begin update public.offers set portions=4 where id=o1; get diagnostics c=row_count; r:=r||('K ändert Portionen: '||c||' Zeile (erwartet 1)');
  exception when others then r:=r||('K ändert Portionen: FEHLER '||sqlerrm); end;
  begin update public.offers set status='cancelled' where id=o1; get diagnostics c=row_count; r:=r||('K storniert: '||c||' Zeile (erwartet 1)');
  exception when others then r:=r||('K storniert: FEHLER '||sqlerrm); end;
  begin update public.offers set status='open' where id=o1; get diagnostics c=row_count; r:=r||('K öffnet storniertes wieder: '||c||' Zeilen (erwartet 0)');
  exception when others then r:=r||('K öffnet storniertes wieder: blockiert – '||sqlerrm); end;
  select count(*) into c from public.profiles; r:=r||('K sieht Profile vor Reservation (erwartet 1): '||c);
  execute 'reset role';

  perform set_config('request.jwt.claims', json_build_object('sub',t,'role','authenticated')::text, true);
  execute 'set local role authenticated';
  begin select * into rec from public.reserve_offer(o2); r:=r||('T reserviert per RPC: '||rec.status||' (erwartet reserved)');
  exception when others then r:=r||('T reserviert per RPC: FEHLER '||sqlerrm); end;
  execute 'reset role';

  perform set_config('request.jwt.claims', json_build_object('sub',k,'role','authenticated')::text, true);
  execute 'set local role authenticated';
  select count(*) into c from public.profiles where id=t; r:=r||('K sieht Abnehmer-Profil nach Reservation (erwartet 1): '||c);
  begin update public.offers set portions=3 where id=o2; get diagnostics c=row_count; r:=r||('K ändert reserviertes Angebot (Portionen): '||c||' Zeile (erwartet 1)');
  exception when others then r:=r||('K ändert reserviertes: FEHLER '||sqlerrm); end;
  begin select * into rec from public.mark_picked(o2); r:=r||('K markiert abgeholt per RPC: '||rec.status||' (erwartet picked)');
  exception when others then r:=r||('K mark_picked: FEHLER '||sqlerrm); end;
  begin update public.offers set note='x' where id=o2; get diagnostics c=row_count; r:=r||('K ändert abgeholtes Angebot: '||c||' Zeilen (erwartet 0)');
  exception when others then r:=r||('K ändert abgeholtes: blockiert – '||sqlerrm); end;
  execute 'reset role';

  perform set_config('request.jwt.claims', json_build_object('sub',u,'role','authenticated')::text, true);
  execute 'set local role authenticated';
  select count(*) into c from public.profiles; r:=r||('U (nicht frei) sieht Profile (erwartet 1): '||c);
  select count(*) into c from public.offers; r:=r||('U sieht Angebote (erwartet 0): '||c);
  execute 'reset role';

  perform set_config('request.jwt.claims','{"role":"anon"}',true);
  execute 'set local role anon';
  begin select count(*) into c from public.offers; r:=r||('anon Angebote (erwartet 0): '||c); exception when others then r:=r||('anon Angebote: '||sqlerrm); end;
  begin select count(*) into c from public.profiles; r:=r||('anon Profile (erwartet 0): '||c); exception when others then r:=r||('anon Profile: '||sqlerrm); end;
  execute 'reset role';

  delete from public.offers where kitchen_id=k;
  delete from public.profiles where id in (k,t,u);
  delete from auth.users where id in (k,t,u);
  for c in 1..array_length(r,1) loop insert into public.rls_test_002 values (c, r[c]); end loop;
end $$;
