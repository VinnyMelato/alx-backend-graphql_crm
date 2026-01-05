#!/bin/bash
# Delete customers with no orders in the last year and log the count
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MANAGE_PY="$PROJECT_ROOT/manage.py"
LOGFILE="/tmp/customer_cleanup_log.txt"

DELETED=$(python3 "$MANAGE_PY" shell -c "from datetime import timedelta; from django.utils import timezone; from django.db.models import Max, Q; from crm.models import Customer; cutoff=timezone.now()-timedelta(days=365); qs=Customer.objects.annotate(last_order=Max('orders__order_date')).filter(Q(last_order__lt=cutoff)|Q(last_order__isnull=True)); count=qs.count(); qs.delete(); print(count)" 2>/dev/null)
echo "$(date '+%Y-%m-%d %H:%M:%S'): Deleted ${DELETED:-0} customers" >> "$LOGFILE"
#!/bin/bash
# Delete customers with no orders in the past year and log the number deleted
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DELETED_COUNT=$(python manage.py shell -c "from django.utils import timezone; from crm.models import Customer; import datetime; cutoff=timezone.now()-datetime.timedelta(days=365); ids=[c.id for c in Customer.objects.all() if (not c.order_set.exists()) or (c.order_set.order_by('-order_date').first().order_date < cutoff)]; Customer.objects.filter(id__in=ids).delete(); print(len(ids))")
echo "${TIMESTAMP}: Deleted ${DELETED_COUNT} customers" >> /tmp/customer_cleanup_log.txt
