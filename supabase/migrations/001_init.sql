create extension if not exists vector with schema extensions;

-- RAG: Wissensbasis (Format des n8n Supabase Vector Store)
create table public.documents (
  id bigserial primary key,
  content text,
  metadata jsonb,
  embedding extensions.vector(1536)
);

create or replace function public.match_documents (
  query_embedding extensions.vector(1536),
  match_count int default null,
  filter jsonb default '{}'
) returns table (id bigint, content text, metadata jsonb, similarity float)
language plpgsql
set search_path = public, extensions
as $$
begin
  return query
  select d.id, d.content, d.metadata, 1 - (d.embedding <=> query_embedding) as similarity
  from public.documents d
  where d.metadata @> filter
  order by d.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Ein Prüflauf pro Verordnung
create table public.pruefungen (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  verordnung_ref text not null,
  eingabe jsonb not null,
  gesamtstatus text check (gesamtstatus in ('gruen','gelb','rot')),
  absetzungsrisiko_eur numeric(10,2),
  zusammenfassung text,
  dauer_ms integer,
  freigabe text
);

-- Ein Befund pro Prüfpunkt und Agent
create table public.befunde (
  id bigserial primary key,
  pruefung_id uuid not null references public.pruefungen(id) on delete cascade,
  agent text not null check (agent in ('formal','diagnose','menge','frist')),
  feld text not null,
  status text not null check (status in ('ok','fehlt','fehlerhaft','hinweis')),
  fundstelle text,
  korrekturhinweis text,
  created_at timestamptz not null default now()
);
create index on public.befunde (pruefung_id);

-- Synthetische Testfälle für den Evaluationsbericht
create table public.testfaelle (
  id bigserial primary key,
  name text not null,
  verordnung jsonb not null,
  erwartete_befunde jsonb not null,
  beschreibung text
);

-- Gesundheitskontext: RLS an, keine öffentlichen Policies. n8n nutzt den service_role-Schlüssel.
alter table public.documents enable row level security;
alter table public.pruefungen enable row level security;
alter table public.befunde enable row level security;
alter table public.testfaelle enable row level security;
