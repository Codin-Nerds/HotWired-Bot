CREATE TABLE blacklist (
    guild_ids bigint[] NOT NULL,
    user_ids bigint[] NOT NULL
);


ALTER TABLE blacklist OWNER TO {owner};

CREATE TABLE dungeon (
    guild_id bigint NOT NULL,
    minimum_days integer NOT NULL,
    dungeon_role_id bigint NOT NULL,
    mod_status integer NOT NULL,
    announcement_channel bigint NOT NULL,
    mod_message text NOT NULL,
    bypass_list bigint[] NOT NULL,
    dungeon_status boolean NOT NULL
);


ALTER TABLE dungeon ADD CONSTRAINT unique_dungeon
  UNIQUE (guild_id);

ALTER TABLE dungeon OWNER TO {owner};

CREATE TABLE lock (
    guild_id bigint NOT NULL,
    lock_state integer,
    link_state integer
);


ALTER TABLE public.lock ALTER lock_state SET DEFAULT 0;
ALTER TABLE public.lock ALTER link_state SET DEFAULT 0;

ALTER TABLE lock ADD CONSTRAINT lock_unique
  UNIQUE (guild_id);

ALTER TABLE lock OWNER TO {owner};

CREATE TABLE prefixes (
    ctx_id bigint NOT NULL,
    prefix text NOT NULL
);


ALTER TABLE prefixes ADD CONSTRAINT prefixes_unique
  UNIQUE (ctx_id);

ALTER TABLE prefixes OWNER TO {owner};

CREATE TABLE smartreact (
    guild_id bigint NOT NULL
);


ALTER TABLE smartreact ADD CONSTRAINT unique_smartreact
  UNIQUE (guild_id);

ALTER TABLE smartreact OWNER TO {owner};

CREATE TABLE subscribe (
    guild_id bigint NOT NULL,
    role_id bigint NOT NULL
);


ALTER TABLE subscribe ADD CONSTRAINT unique_subscribe
  UNIQUE (guild_id);

ALTER TABLE subscribe OWNER TO {owner};
