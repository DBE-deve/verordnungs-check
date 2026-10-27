-- Ergebnisse der Testbatterie (Soll/Ist je Fall und Wiederholung), angelegt am 27.10.2026
create table if not exists public.testlaeufe (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  lauf text not null,                 -- Kennung des Batterielaufs, z. B. 2026-10-27-cloud
  workflow_id text,
  testfall_id bigint references public.testfaelle(id),
  fall text not null,
  quelle text,                        -- seed | testbatterie
  set text,                           -- S | E | D
  wiederholung int not null default 1,
  soll text,
  ist text,
  ampel_ok boolean,
  befunde_ok boolean,
  fehlende_befunde jsonb,
  kritischer_fehlalarm boolean,
  dauer_ms int,
  fehler text,
  antwort jsonb
);
alter table public.testlaeufe enable row level security;
comment on table public.testlaeufe is 'Ergebnisse der Testbatterie (Soll/Ist je Fall und Wiederholung)';
