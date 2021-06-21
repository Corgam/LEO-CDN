# Schema
# id;type;lat1;lon1;lat2;lon2;lat3;lon3;lat4;lon4;lat5;lon5;lat6;lon6
import h3
import pandas as pd


def get_type(length):
    if length == 6:
        return "pent"
    elif length == 7:
        # assume we only have these two
        return "hex"
    elif length == 8:
        return "hept"


def generate_keygroups():
    # TODO fix other layers
    # columns = ["id", "type", "lat1", "lon1", "lat2", "lon2", "lat3", "lon3", "lat4", "lon4", "lat5", "lon5", "lat6", "lon6", "lat7", "lon7"]
    columns = ["id", "type", "lat1", "lon1", "lat2", "lon2", "lat3", "lon3", "lat4", "lon4", "lat5", "lon5", "lat6", "lon6", "lat7", "lon7", "lat8", "lon8"]

    df = pd.DataFrame(columns=columns)

    hex_list = list()
    h3_address = h3.geo_to_h3(0, 0, 1)  # lat, lng, hex resolution
    hex_list.append([h3_address])
    for i in range(0, 40):
        hex_list.append(list(h3.k_ring_distances(h3_address, 40)[i]))
    hex_list = [item for sublist in hex_list for item in sublist]
    for hex in hex_list:
        print(hex)
        coords = h3.h3_to_geo_boundary(hex, geo_json=True)
        polygon_type = get_type(len(coords))
        if polygon_type is None:
            continue
        print(coords)
        row = list()
        row.append(hex)
        row.append(polygon_type)
        for coord in coords:
            row.append(coord[1])  # lon
            row.append(coord[0])  # lat
        if polygon_type == "pent":
            # because pandas dataframes need the correct amount of columns
            row += ["", "", "", ""]
        if polygon_type == "hex":
            row += ["", ""]
        print(row)
        print(len(row))

        df.loc[len(df)] = row
    df.to_csv("../CSV/keygroups_2.csv", index=False, sep=';')


if __name__ == "__main__":
    generate_keygroups()
