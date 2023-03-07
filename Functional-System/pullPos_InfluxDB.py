
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from flightsql import FlightSQLClient
import pandas as pd

# "static" variable
# query_client = FlightSQLClient()

query = """SELECT *
FROM "mqtt_consumer"
WHERE
time >= timestamp '2023-03-07T23:00:00.000Z' AND time <= timestamp '2023-03-07T23:20:00.000Z'
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
    # df = df.mutate(q = 100/int(p))
    # df['q'] = df.transform(lambda x: 100/x['position_quality'])
    print(df)
    # df = df.select() #limit data?
    return df #send it back up

# test harness
def main():
    client = init_client()

    df = pullData(client)
    print(df.info())
    print(df.head())

if __name__ == '__main__':
    main()