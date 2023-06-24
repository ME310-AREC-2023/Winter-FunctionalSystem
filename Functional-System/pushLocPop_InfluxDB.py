
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd

token = os.environ.get("INFLUXDB_TOKEN")
org = "ME 310 AREC"
url = "https://us-east-1-1.aws.cloud2.influxdata.com"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

# choose bucket
bucket="test-Upload"

# Define the write api
write_api = write_client.write_api(write_options=SYNCHRONOUS)

def writeLocationPop(populaar):
    # point = (
    #     Point("LocationPop-test")
    #     .tag("Prototype", "FunctionalSystem")
    #     .field()
    # )
    # write_api.write(bucket=bucket, org=org, record = point)

    # give it time
    # populaar.set_index("_time")
    populaar['data_frame_measurement_name'] = {'Prototype':'Funct'}
    write_api.write(bucket=bucket,org=org, record = populaar)



# test harness
def main():
    df = pd.DataFrame({'AREC':[15], 'Volvo':[10], 'Avatar':[20], 'JnJ': [25], 'Travelling':[30]})
    df = df.T #transpose for data clarity?
    plot = df.plot.bar(legend=False, rot=0, \
                       title= f"Location Popularity in ME310 at {time.strftime('%H:%M')}",\
                       ylabel='% Time Spent with each Team')
    fig = plot.get_figure()
    fig.savefig('images/test-LocPop.png')

    # writeLocationPop(df)

if __name__ == '__main__':
    main()