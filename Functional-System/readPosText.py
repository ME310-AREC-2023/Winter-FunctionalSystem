
import sys
import pandas as pd

def read_DTRLS_logfile(filename):
    points = []
    df = pd.DataFrame()
    with open(filename) as f:
        for line in f:
            linex_extract = line.split("x=")
            x_p = -int(linex_extract[1][:5])/10
            liney_extract = line.split("y=")
            y_p = int(liney_extract[1][:4])/10
            liney_extract = line.split("q=")
            q = 100*1/int(liney_extract[1][:2])
            points.append((q, x_p, y_p))
            new_df = pd.DataFrame({'position_x': [x_p], 'position_y': [y_p], 'position_quality':[q]})
            df = pd.concat([df, new_df], ignore_index=True, axis=0, join='outer')
    # print(df)
    return df
