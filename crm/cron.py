from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
        f.write(f"{timestamp} CRM is alive\n")
    try:
        client = Client(transport=RequestsHTTPTransport(url='http://localhost:8000/graphql'))
        result = client.execute(gql('{ hello }'))
        if result['hello'] == 'World':
            with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                f.write(f"{timestamp} GraphQL endpoint responsive\n")
    except Exception as e:
        with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
            f.write(f"{timestamp} Heartbeat check error: {str(e)}\n")


def update_low_stock():
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
                transport = RequestsHTTPTransport(url='http://localhost:8000/graphql')
                client = Client(transport=transport, fetch_schema_from_transport=True)
                mutation = gql('''
                mutation {
                    updateLowStockProducts {
                        updatedProducts {
                            name
                            stock
                        }
                        message
                        success
                    }
                }
                ''')
                result = client.execute(mutation)
                data = result.get('updateLowStockProducts') or {}
                updated = data.get('updatedProducts', [])
                if updated:
                        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                                for p in updated:
                                        f.write(f"{timestamp}: {p.get('name')} stock updated to {p.get('stock')}\n")
        except Exception as e:
                with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                        f.write(f"{timestamp}: Error updating low stock products: {str(e)}\n")
