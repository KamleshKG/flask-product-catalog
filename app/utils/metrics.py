from prometheus_client import Counter, Gauge, Histogram

# Product metrics
PRODUCT_VIEWS = Counter('product_views_total', 'Total product views', ['product_id'])
PRODUCT_UPDATES = Counter('product_updates_total', 'Total product updates')
PRODUCT_CREATES = Counter('product_creates_total', 'Total products created')

# Performance metrics
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])
DATABASE_QUERY_TIME = Histogram('db_query_duration_seconds', 'Database query time')

# System metrics
ACTIVE_USERS = Gauge('active_users', 'Currently active users')