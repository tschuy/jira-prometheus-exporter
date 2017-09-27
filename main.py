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

    healthy = len([status for status in health_statuses if status == True])
    unhealthy = len([status for status in health_statuses if status != True])
    g.labels('healthy').set(healthy)
    g.labels('unhealthy').set(unhealthy)
    logging.info("finished updating health ({} healthy, {} unhealthy)".format(healthy, unhealthy))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info("starting prometheus metrics server")
    start_http_server(8000)
    while True:
        check_health(os.environ.get('JIRAENDPOINT', 'http://localhost:8080'), os.environ['JIRAUSER'], os.environ['JIRAPASSWORD'])
        time.sleep(15)