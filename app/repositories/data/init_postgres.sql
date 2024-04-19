-- 创建uuid扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- 创建pgcrypto扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 更行数据时更新updated_at
CREATE FUNCTION update_updated_at_column() RETURNS trigger LANGUAGE plpgsql AS
$$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        NEW.updated_at = CURRENT_TIMESTAMP(0);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$;

-- 用户
CREATE TABLE cube_accounts
(
    id         UUID                     DEFAULT UUID_GENERATE_V4()          NOT NULL CONSTRAINT pk_cube_accounts_id PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0)        NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0)        NOT NULL,
    uid        VARCHAR(32)                                                  NOT NULL,
    name       VARCHAR(128)                                                 NOT NULL,
    email      VARCHAR(128)                                                 NOT NULL,
    password   VARCHAR(128)                                                 NOT NULL,
    avatar     VARCHAR(256),
    status     VARCHAR(32)              DEFAULT 'active'::CHARACTER VARYING NOT NULL
);
CREATE UNIQUE INDEX idx_cube_accounts_uid ON cube_accounts (uid);
CREATE UNIQUE INDEX idx_cube_accounts_email ON cube_accounts (email);
CREATE TRIGGER set_cube_accounts_updated_at
    BEFORE UPDATE
    ON cube_accounts
    FOR EACH ROW
EXECUTE procedure update_updated_at_column();

-- 工作区
CREATE TABLE cube_workspaces
(
    id          UUID                     DEFAULT UUID_GENERATE_V4()   NOT NULL CONSTRAINT pk_cube_teams_id PRIMARY KEY,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
    uid         VARCHAR(32)                                           NOT NULL,
    creator_uid VARCHAR(32)                                           NOT NULL,
    name        VARCHAR(128)                                          NOT NULL,
    description VARCHAR(512),
    is_personal SMALLINT                 DEFAULT '0'::SMALLINT        NOT NULL,
    iv          VARCHAR(32)                                           NOT NULL,
    is_deleted  SMALLINT                 DEFAULT '0'::SMALLINT        NOT NULL
);
CREATE UNIQUE INDEX idx_cube_workspaces_uid ON cube_workspaces (uid);
CREATE TRIGGER set_cube_workspaces_updated_at
    BEFORE UPDATE
    ON cube_workspaces
    FOR EACH ROW
EXECUTE procedure update_updated_at_column();

-- 工作区成员
CREATE TABLE cube_workspace_memberships
(
    id            UUID                     DEFAULT UUID_GENERATE_V4()           NOT NULL CONSTRAINT pk_cube_workspace_memberships_id PRIMARY KEY,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0)         NOT NULL,
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0)         NOT NULL,
    uid           VARCHAR(32)                                                   NOT NULL,
    workspace_uid VARCHAR(32)                                                   NOT NULL,
    member_uid    VARCHAR(32)                                                   NOT NULL,
    member_role   VARCHAR(32)                                                   NOT NULL,
    member_status VARCHAR(32)              DEFAULT 'pending'::CHARACTER VARYING NOT NULL
);
CREATE UNIQUE INDEX idx_cube_workspace_memberships_uid ON cube_workspace_memberships (uid);
CREATE INDEX idx_cube_workspace_memberships_workspace_uid ON cube_workspace_memberships (workspace_uid, member_uid, member_status);
CREATE INDEX idx_cube_workspace_memberships_member_uid ON cube_workspace_memberships (member_uid, member_status, workspace_uid);
CREATE TRIGGER set_cube_workspace_memberships_updated_at
    BEFORE UPDATE
    ON cube_workspace_memberships
    FOR EACH ROW
EXECUTE procedure update_updated_at_column();
