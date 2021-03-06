"""Configures KSQL to combine station and turnstile data"""
import json
import logging

import requests

import topic_check


logger = logging.getLogger(__name__)


KSQL_URL = "http://localhost:8088"

# Create a turnstile table and a summary table with the counts per station 
KSQL_STATEMENT = """
CREATE TABLE turnstile (
    station_id int,
    station_name varchar,
    line varchar
) WITH (
    KAFKA_TOPIC='station.turnstiles',
    VALUE_FORMAT='avro',
    KEY='station_id'
);

CREATE TABLE turnstile_summary
WITH (value_format = 'json') AS
    SELECT 
        station_id, 
        COUNT(STATION_ID) as count
    FROM 
        turnstile
    GROUP BY 
        station_id;
"""


def execute_statement():
    """Executes the KSQL statement against the KSQL API"""
    if topic_check.topic_exists("TURNSTILE_SUMMARY") is True:
        return

    logging.debug("executing ksql statement...")

    resp = requests.post(
        f"{KSQL_URL}/ksql",
        headers={"Content-Type": "application/vnd.ksql.v1+json"},
        data=json.dumps(
            {
                "ksql": KSQL_STATEMENT,
                "streamsProperties": {"ksql.streams.auto.offset.reset": "earliest"},
            }
        ),
    )

    # Ensure that a 2XX status code was returned
    resp.raise_for_status()


if __name__ == "__main__":
    execute_statement()
