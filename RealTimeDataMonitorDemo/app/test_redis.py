import redis

r = redis.Redis(host='localhost', port=6379, db=0)
print(r.ping())  # 如果输出 True，说明Redis已连通