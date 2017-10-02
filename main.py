from prometheus_client import start_http_server, Gauge
import logging
import os
import random
import requests
import time

from prometheus_client import Gauge
g = Gauge('jira_health_checks', 'Number of healthy/unhealthy Jira health checks', ['health'])

def check_health(endpoint, user, password):
    logging.info("updating health")
    process_id_endpoint = "{}/rest/supportHealthCheck/1.0/check/process/".format(endpoint)
    r = requests.post(process_id_endpoint, auth=(user, password))
    process_id = r.json()['processId']

    health_check_endpoint = "{}/rest/supportHealthCheck/1.0/check/process/{}/results".format(endpoint, process_id)
    r = requests.get(health_check_endpoint, auth=(user, password))

    health_statuses = [status['isHealthy'] for status in r.json()['statuses']]

    healthy = health_statuses.count(True)
    unhealthy = health_statuses.count(False)
    g.labels('healthy').set(healthy)
    g.labels('unhealthy').set(unhealthy)
    logging.info("finished updating health ({} healthy, {} unhealthy)".format(healthy, unhealthy))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info("starting prometheus metrics server")
    start_http_server(8000)
    while True:
        try:
            check_health(os.environ.get('JIRAENDPOINT', 'http://localhost:8080'), os.environ['JIRAUSER'], os.environ['JIRAPASSWORD'])
        except Exception as e:
            g.labels('healthy').set(0)
            g.labels('unhealthy').set(1)
            logging.warn(e)
        time.sleep(15)
