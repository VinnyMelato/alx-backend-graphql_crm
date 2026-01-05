#!/usr/bin/env python3
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(url='http://localhost:8000/graphql')
client = Client(transport=transport, fetch_schema_from_transport=True)
cutoff = datetime.now() - timedelta(days=7)

query = gql('''
query {
  allOrders(first: 1000) {
    edges {
      node {
        id
        orderDate
        customer { email }
      }
    }
  }
}
''')

try:
    result = client.execute(query)
    orders = []
    for edge in result.get('allOrders', {}).get('edges', []):
        node = edge.get('node') or {}
        od = node.get('orderDate')
        if not od:
            continue
        try:
            od_dt = datetime.fromisoformat(od)
        except Exception:
            # skip unparsable dates
            continue
        if od_dt >= cutoff:
            orders.append({'id': node.get('id'), 'email': node.get('customer', {}).get('email')})

    with open('/tmp/order_reminders_log.txt', 'a') as f:
        for o in orders:
            f.write(f"{datetime.now().isoformat()}: Order {o['id']} - Customer: {o['email']}\n")

    print("Order reminders processed!")
except Exception as e:
    print(f"Error fetching orders: {e}")
