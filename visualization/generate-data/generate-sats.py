# Schema
# id;lat;lon;keygroupID
import pandas as pd
import numpy as np
from h3 import h3


def generate_satellites():
    columns = ['id', 'lat', 'lon', 'keygroupID']
    for resolution in range(2):
        for i in range(5):
            final_df = pd.DataFrame(columns=columns)
            df = pd.read_csv(f'../CSV/satellites_{i}_xyz.csv',  names=['x', 'y', 'z'])
            for index, row in df.iterrows():
                new_row = list()
                new_row.append(f"satellite{index}")
                radius = 6371000
                lon = np.degrees(np.arctan2(row['y'], row['x']))
                lat = np.degrees(np.arcsin(row['z'] / radius))
                new_row.append(lat)
                new_row.append(lon)
                new_keygroup_name = h3.geo_to_h3(lat, lon, resolution)  # is the same as h3 area
                new_row.append(new_keygroup_name)
                final_df.loc[len(final_df)] = new_row
            print(final_df)
            final_df.to_csv(f"../CSV/satellites_{resolution}_{i}.csv", index=False, sep=';')


if __name__ == "__main__":
    generate_satellites()