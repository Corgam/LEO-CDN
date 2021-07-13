import json

import numpy as np
import pandas as pd
import toml
import umap.umap_ as umap
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from util import transform_geo_to_xyz

with open("./config.toml") as f:
    config = toml.load(f)

# TODO: Read the cities list from config
input_file = config["general"]["gsts_list"]
output_file = config["workload"]["output_file"]
file_size_output_file = config["workload"]["file_size_output_file"]

print(f"Reading input file from {input_file}")
df_gst = pd.read_csv(input_file)


def row_transform_geo_to_xyz(row):
    lat = row.lat
    lon = row.lng
    return transform_geo_to_xyz(lat, lon)


print(f"Transforming ground station lat/lon to xyz coordinates...")
df_gst["x"], df_gst["y"], df_gst["z"] = zip(
    *df_gst.apply(row_transform_geo_to_xyz, axis=1)
)

reducer = umap.UMAP(n_components=3, n_neighbors=100)

X_raw = df_gst[["x", "y", "z", "iso2"]].to_numpy()

print(f"Preprocessing ground stations...")
num_cols = [0, 1, 2]
cat_cols = [3]
pipeline = ColumnTransformer(
    [
        ("num_transformer", StandardScaler(), num_cols),
        ("cat_transformer", OneHotEncoder(), cat_cols),
    ]
)
X = pipeline.fit_transform(X_raw)

print(f"Translating ground station data into embedding space...")
X_transformed = reducer.fit_transform(X)


xmin = np.min(X_transformed[:, 0])
xmax = np.max(X_transformed[:, 0])

ymin = np.min(X_transformed[:, 1])
ymax = np.max(X_transformed[:, 1])

zmin = np.min(X_transformed[:, 1])
zmax = np.max(X_transformed[:, 1])

xx, yy, zz = np.mgrid[xmin:xmax:10j, ymin:ymax:10, zmin:zmax:10j]

# file_id is index in file_positions
file_positions = np.vstack([xx.ravel(), yy.ravel(), zz.ravel()])


def calculate_distance_to_files(gst_coords, files_coords):
    dists = []
    for f_coords in files_coords.T:
        d = np.linalg.norm(gst_coords - f_coords)
        dists.append(d)
    return np.array(dists)


print("Computing files popularities for all ground stations...")
gst_file_orders = {}
for index, row in df_gst.iterrows():
    gst_id = row.id
    print(f"Computing file popularity for ground station {gst_id}...")
    gst_coords = row[["x", "y", "z"]].to_numpy()
    D = calculate_distance_to_files(gst_coords, file_positions)

    file_order = D.argsort()
    gst_file_orders[gst_id] = file_order.tolist()


# https://www.researchgate.net/publication/227252035_Web_Workload_Characterization_Ten_Years_Later suggest pareto distribution with alpha~1
# https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjhpZj0wMzxAhUhg_0HHXalChQQFjAAegQIAhAD&url=https%3A%2F%2Fwww.cc.gatech.edu%2F~dovrolis%2FCourses%2F8803_F03%2Famogh.ppt&usg=AOvVaw3OA7_OuBWI0B1lMUOV9dVh suggests lognormal model or  hybrid model with lognormal distribution with a Pareto tail
file_sizes = np.ceil(
    np.random.pareto(int(config["workload"]["pareto_alpha"]), file_positions.shape[0])
)

df_fs = pd.DataFrame(data=file_sizes, columns=["file_size"])
df_fs.index.name = "file_id"
df_fs.to_csv(file_size_output_file, mode="w", index=True)

print(f"Saving file popularity output file to {output_file}...")
with open(output_file, "w") as f:
    json.dump(gst_file_orders, f)
