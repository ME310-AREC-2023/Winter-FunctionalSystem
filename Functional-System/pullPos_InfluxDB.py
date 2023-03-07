
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from flightsql import FlightSQLClient
import pandas as pd

query = """SELECT *
FROM "mqtt_consumer"
WHERE
time >= now() - interval '30 minutes'
AND
("position_x" IS NOT NULL)"""


def init_client():
    # Define the query client
    query_client = FlightSQLClient(
        host = "us-east-1-1.aws.cloud2.influxdata.com",
        token = os.environ.get("INFLUXDB_TOKEN"),
        metadata={"bucket-name": "test-UWB-tags"}
    )
    return query_client
def pullData(query_client):
    # Execute the query
    info = query_client.execute(query)
    reader = query_client.do_get(info.endpoints[0].ticket)

    #show data
    data = reader.read_all()
    df = data.to_pandas().sort_values(by="time")
    # print(df)
    # df = df.select() #limit data?
    return df #send it back up

# test harness
def main():
    client = init_client()

    pullData(client)

if __name__ == '__main__':
    main()