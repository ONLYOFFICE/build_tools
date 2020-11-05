--
-- Create schema onlyoffice
--

-- CREATE DATABASE onlyoffice ENCODING = 'UTF8' CONNECTION LIMIT = -1;

-- ----------------------------
-- Table structure for doc_changes
-- ----------------------------
CREATE TABLE IF NOT EXISTS "public"."doc_changes" (
"id" varchar(255) COLLATE "default" NOT NULL,
"change_id" int4 NOT NULL,
"user_id" varchar(255) COLLATE "default" NOT NULL,
"user_id_original" varchar(255) COLLATE "default" NOT NULL,
"user_name" varchar(255) COLLATE "default" NOT NULL,
"change_data" text COLLATE "default" NOT NULL,
"change_date" timestamp without time zone NOT NULL,
PRIMARY KEY ("id", "change_id")
)
WITH (OIDS=FALSE);

-- ----------------------------
-- Table structure for task_result
-- ----------------------------
CREATE TABLE IF NOT EXISTS "public"."task_result" (
"id" varchar(255) COLLATE "default" NOT NULL,
"status" int2 NOT NULL,
"status_info" int4 NOT NULL,
"last_open_date" timestamp without time zone NOT NULL,
"user_index" int4 NOT NULL DEFAULT 1,
"change_id" int4 NOT NULL DEFAULT 0,
"callback" text COLLATE "default" NOT NULL,
"baseurl" text COLLATE "default" NOT NULL,
PRIMARY KEY ("id")
)
WITH (OIDS=FALSE);

CREATE OR REPLACE FUNCTION merge_db(_id varchar(255), _status int2, _status_info int4, _last_open_date timestamp without time zone, _user_index int4, _change_id int4, _callback text, _baseurl text, OUT isupdate char(5), OUT userindex int4) AS
$$
DECLARE
	t_var "public"."task_result"."user_index"%TYPE;
BEGIN
	LOOP
		-- first try to update the key
		-- note that "a" must be unique
		UPDATE "public"."task_result" SET last_open_date=_last_open_date, user_index=user_index+1 WHERE id = _id RETURNING user_index into userindex;
		IF found THEN
			isupdate := 'true';
			RETURN;
		END IF;
		-- not there, so try to insert the key
		-- if someone else inserts the same key concurrently,
		-- we could get a unique-key failure
		BEGIN
			INSERT INTO "public"."task_result"(id, status, status_info, last_open_date, user_index, change_id, callback, baseurl) VALUES(_id, _status, _status_info, _last_open_date, _user_index, _change_id, _callback, _baseurl) RETURNING user_index into userindex;
			isupdate := 'false';
			RETURN;
		EXCEPTION WHEN unique_violation THEN
			-- do nothing, and loop to try the UPDATE again
		END;
	END LOOP;
END;
$$
LANGUAGE plpgsql;
