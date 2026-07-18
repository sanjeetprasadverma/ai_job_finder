FROM apache/airflow:latest
# FROM apache/airflow:2.10.5


USER root

COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

# Switch back to airflow user
USER airflow

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/entrypoint.sh"]