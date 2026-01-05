#!/usr/bin/env python3
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

client = Client(transport=RequestsHTTPTransport(url='http://localhost:8000/graphql'), fetch_schema_from_transport=True)
seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()

query = gql('''
query RecentOrders($orderDateAfter: String!) {
  recentOrders(orderDateAfter: $orderDateAfter) {
    id
    customer { email }
  }
}
''')

result = client.execute(query, variable_values={'orderDateAfter': seven_days_ago})
with open('/tmp/order_reminders_log.txt', 'a') as f:
    for order in result['recentOrders']:
        f.write(f"{datetime.now().isoformat()}: Order {order['id']} - Customer: {order['customer']['email']}\n")
print("Order reminders processed!")
