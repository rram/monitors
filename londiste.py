#!/usr/bin/python

import time

import psycopg2

import alerts


CONFIG_SECTION = 'londiste'


def watch_replication(servers, ignored_prefixes, threshold, interval):
    while True:
        for server in servers:
            connection = psycopg2.connect(server)
            cursor = connection.cursor()
            cursor.execute("SELECT consumer_name, last_seen " +
                           "FROM pgq.get_consumer_info()")

            for consumer, last_seen in cursor:
                if any(consumer.startswith(prefix)
                       for prefix in ignored_prefixes):
                    continue

                last_seen = last_seen.total_seconds()
                if last_seen > threshold:
                    alerts.harold.alert("%srepl" % consumer,
                                        "%s has not been seen for %s seconds" % 
                                        (consumer, last_seen))

            cursor.close()
            connection.close()

        alerts.harold.heartbeat("monitor_replication", interval * 2)
        time.sleep(interval)


def main():
    # expects a config section like the following
    # [londiste]
    # threshold = 1800
    # interval = 30
    # ignore_prefix = ... , ...
    # master.* = hostname=some-host user=sdf password=slkdfj dbname=reddit
    alerts.init()

    connection_strings = [value for key, value in
                          alerts.config.items(CONFIG_SECTION)
                          if key.startswith("master")]
    interval = alerts.config.getint(CONFIG_SECTION, "interval")
    threshold = alerts.config.getint(CONFIG_SECTION, "threshold")
    ignored_prefixes = [host.strip() for host in
                         alerts.config.get(CONFIG_SECTION, "ignore_prefix").split(',')]

    watch_replication(connection_strings, ignored_prefixes, threshold, interval)


if __name__ == "__main__":
    main()
