import multiprocessing

bind = "0.0.0.0:8000"
workers = (2 * multiprocessing.cpu_count()) + 1
worker_class = "gevent"
accesslog = "-"
loglevel = "error"
forwarded_allow_ips = "*"
proxy_allow_ips = "*"
proxy_protocol = True
max_requests = 128
