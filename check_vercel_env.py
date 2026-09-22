import os
from urllib.parse import urlsplit

u = os.getenv("DATABASE_URL")

print("DATABASE_URL exists:", bool(u))

if u:
    p = urlsplit(u)
    print("scheme=", p.scheme)
    print("host=", p.hostname)
    print("port=", p.port)
    print("database=", p.path)
