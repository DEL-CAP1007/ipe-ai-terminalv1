CREATE TABLE IF NOT EXISTS service_account_role (
    service_id UUID REFERENCES service_account(id),
    role_id UUID REFERENCES role(id),
    PRIMARY KEY(service_id, role_id)
);
