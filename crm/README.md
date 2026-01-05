# CRM Celery Tasks

Setup and running instructions for Celery report task

1. Install Redis and Python dependencies

```bash
# On Ubuntu:
sudo apt-get install redis-server
pip install -r requirements.txt
```

2. Run migrations

```bash
python manage.py migrate
```

3. Start Redis

```bash
sudo service redis-server start
```

4. Start Celery worker and beat

```bash
# Start worker
celery -A crm worker -l info

# Start beat
celery -A crm beat -l info
```

5. Verify logs

Check `/tmp/crm_report_log.txt` for weekly report entries.
