#!/bin/bash
# Delete customers with no orders in the past year and log the number deleted
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DELETED_COUNT=$(python manage.py shell -c "from django.utils import timezone; from crm.models import Customer; import datetime; cutoff=timezone.now()-datetime.timedelta(days=365); ids=[c.id for c in Customer.objects.all() if (not c.order_set.exists()) or (c.order_set.order_by('-order_date').first().order_date < cutoff)]; Customer.objects.filter(id__in=ids).delete(); print(len(ids))")
echo "${TIMESTAMP}: Deleted ${DELETED_COUNT} customers" >> /tmp/customer_cleanup_log.txt
