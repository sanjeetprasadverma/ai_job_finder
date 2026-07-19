#!/bin/bash
set -e

PASSWORD_FILE="${AIRFLOW_HOME}/simple_auth_manager_passwords.json.generated"

if [ -n "$AIRFLOW_ADMIN_USER" ] && [ -n "$AIRFLOW_ADMIN_PASSWORD" ]; then
  echo "{\"${AIRFLOW_ADMIN_USER}\": \"${AIRFLOW_ADMIN_PASSWORD}\"}" > "$PASSWORD_FILE"
fi

airflow db migrate

exec airflow standalone