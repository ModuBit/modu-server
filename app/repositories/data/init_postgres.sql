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
CREATE TABLE cube_account
(
    id         UUID                     DEFAULT UUID_GENERATE_V4()          NOT NULL CONSTRAINT pk_cube_account_id PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0)        NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0)        NOT NULL,
    uid        VARCHAR(32)                                                  NOT NULL,
    name       VARCHAR(128)                                                 NOT NULL,
    email      VARCHAR(128)                                                 NOT NULL,
    password   VARCHAR(128)                                                 NOT NULL,
    avatar     VARCHAR(256),
    status     VARCHAR(32)              DEFAULT 'active'::CHARACTER VARYING NOT NULL,
    is_deleted  SMALLINT                DEFAULT '0'::SMALLINT        NOT NULL
);
CREATE UNIQUE INDEX uk_cube_account_uid ON cube_account (uid);
CREATE UNIQUE INDEX uk_cube_account_email ON cube_account (email);
CREATE TRIGGER set_cube_account_updated_at
    BEFORE UPDATE
    ON cube_account
    FOR EACH ROW
EXECUTE procedure update_updated_at_column();

-- 工作区
CREATE TABLE cube_workspace
(
    id          UUID                     DEFAULT UUID_GENERATE_V4()   NOT NULL CONSTRAINT pk_cube_workspace_id PRIMARY KEY,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
    uid         VARCHAR(32)                                           NOT NULL,
    creator_uid VARCHAR(32)                                           NOT NULL,
    name        VARCHAR(128)                                          NOT NULL,
    description VARCHAR(512),
    type        VARCHAR(32)                                           NOT NULL,
    is_deleted  SMALLINT                 DEFAULT '0'::SMALLINT        NOT NULL
);
CREATE UNIQUE INDEX uk_cube_workspace_uid ON cube_workspace (uid);
CREATE TRIGGER set_cube_workspace_updated_at
    BEFORE UPDATE
    ON cube_workspace
    FOR EACH ROW
EXECUTE procedure update_updated_at_column();

-- 工作区成员
CREATE TABLE cube_workspace_membership
(
    id            UUID                     DEFAULT UUID_GENERATE_V4()           NOT NULL CONSTRAINT pk_cube_workspace_membership_id PRIMARY KEY,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0)         NOT NULL,
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0)         NOT NULL,
    uid           VARCHAR(32)                                                   NOT NULL,
    workspace_uid VARCHAR(32)                                                   NOT NULL,
    member_uid    VARCHAR(32)                                                   NOT NULL,
    member_role   VARCHAR(32)                                                   NOT NULL,
    member_status VARCHAR(32)              DEFAULT 'pending'::CHARACTER VARYING NOT NULL,
    is_deleted  SMALLINT                   DEFAULT '0'::SMALLINT        NOT NULL
);
CREATE UNIQUE INDEX uk_cube_workspace_membership_uid ON cube_workspace_membership (uid);
CREATE INDEX idx_cube_workspace_membership_workspace_uid ON cube_workspace_membership (workspace_uid, member_uid, member_status);
CREATE INDEX idx_cube_workspace_membership_member_uid ON cube_workspace_membership (member_uid, member_status, workspace_uid);
CREATE TRIGGER set_cube_workspace_membership_updated_at
    BEFORE UPDATE
    ON cube_workspace_membership
    FOR EACH ROW
EXECUTE procedure update_updated_at_column();

-- LLM Provider 配置
CREATE TABLE cube_llm_provider_config
(
    id            UUID                     DEFAULT UUID_GENERATE_V4()   NOT NULL CONSTRAINT pk_cube_llm_provider_config_id PRIMARY KEY,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
    uid           VARCHAR(32)                                           NOT NULL,
    workspace_uid VARCHAR(32)                                           NOT NULL,
    provider_name  VARCHAR(32)                                           NOT NULL,
    provider_credential VARCHAR                                         NOT NULL,
    is_deleted  SMALLINT                   DEFAULT '0'::SMALLINT        NOT NULL
);
CREATE UNIQUE INDEX uk_cube_llm_provider_uid ON cube_llm_provider_config (uid);
CREATE UNIQUE INDEX uk_cube_llm_provider_space_key ON cube_llm_provider_config (workspace_uid, provider_name);
CREATE TRIGGER set_cube_llm_provider_updated_at
    BEFORE UPDATE
    ON cube_llm_provider_config
    FOR EACH ROW
EXECUTE procedure update_updated_at_column();

-- LLM 系统默认模型配置
CREATE TABLE cube_llm_system_model_config
(
    id            UUID                     DEFAULT UUID_GENERATE_V4()   NOT NULL CONSTRAINT pk_cube_llm_system_model_config_id PRIMARY KEY,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
    uid           VARCHAR(32)                                           NOT NULL,
    workspace_uid VARCHAR(32)                                           NOT NULL,
    model_config  JSONB                                                 NOT NULL,
    is_deleted  SMALLINT                   DEFAULT '0'::SMALLINT        NOT NULL
);
CREATE UNIQUE INDEX uk_cube_llm_system_model_config_uid ON cube_llm_system_model_config (uid);
CREATE UNIQUE INDEX uk_cube_llm_system_model_config_space ON cube_llm_system_model_config (workspace_uid);
CREATE TRIGGER set_cube_llm_system_model_config_updated_at
    BEFORE UPDATE
    ON cube_llm_system_model_config
    FOR EACH ROW
EXECUTE procedure update_updated_at_column();