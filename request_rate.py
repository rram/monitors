#!/usr/bin/python

import sys
import time

from alerts import harold

HEARTBEAT_INTERVAL = 15
ALERT_THRESHOLD = 20

ALERT_RATE_LIMIT = 15
ALERT_GRACE_PERIOD = 5
first_bad_count = {}
last_alert = {}

last_heartbeat = 0
while True:
    line = sys.stdin.readline()
    fields = line.rstrip("\n").split()
    status_code, count = int(fields[-2][:-1]), int(fields[-1])

    now = time.time()

    if status_code >= 500:
        if count >= ALERT_THRESHOLD:
            first_bad_count.setdefault(status_code, now)
            if (now - first_bad_count[status_code] >= ALERT_GRACE_PERIOD and
                last_alert.get(status_code, 0) + ALERT_RATE_LIMIT <= now):
                last_alert[status_code] = now

                harold.alert("request_rate", 
                             "too many %d responses (%d / s)" % (status_code, count))
        else:
            if status_code in first_bad_count:
                del first_bad_count[status_code]

    if (now - last_heartbeat) >= HEARTBEAT_INTERVAL:
        harold.heartbeat("reqrate_monitor", HEARTBEAT_INTERVAL * 2)
        last_heartbeat = now
