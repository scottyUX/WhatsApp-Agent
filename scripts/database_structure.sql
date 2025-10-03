create table users (
  id uuid primary key default gen_random_uuid(),
  phone_number text unique not null,
  name text,
  created_at timestamptz default now()
);

create table messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete set null,
  direction text check (direction in ('incoming', 'outgoing')) not null,
  body text,
  media_url text, -- if the message has an image/audio/etc.
  created_at timestamptz default now()
);
