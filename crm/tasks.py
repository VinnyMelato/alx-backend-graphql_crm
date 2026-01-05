from celery import shared_task
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


@shared_task
def generate_crm_report():
    transport = RequestsHTTPTransport(url='http://localhost:8000/graphql', verify=False)
    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql('''
    query {
      allCustomers(first: 10000) { edges { node { id } } }
      allOrders(first: 10000) { edges { node { id totalAmount } } }
    }
    ''')

    try:
        result = client.execute(query)
        customers = result.get('allCustomers', {}).get('edges', [])
        orders = result.get('allOrders', {}).get('edges', [])

        total_customers = len(customers)
        total_orders = len(orders)
        total_revenue = 0
        for edge in orders:
            node = edge.get('node') or {}
            ta = node.get('totalAmount') or 0
            try:
                total_revenue += float(ta)
            except Exception:
                continue

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(line)
        return line
    except Exception as e:
        return f"Error generating report: {e}"
