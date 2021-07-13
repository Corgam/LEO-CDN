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
    elif length == 9:
        return "oct"
    elif length == 11:
        return "dec"



def generate_keygroups():
    # TODO fix other layers
    # columns = ["id", "type", "lat1", "lon1", "lat2", "lon2", "lat3", "lon3", "lat4", "lon4", "lat5", "lon5", "lat6",
    # "lon6", "lat7", "lon7"]
    columns = ["id", "type", "lat1", "lon1",
                             "lat2", "lon2",
                             "lat3", "lon3",
                             "lat4", "lon4",
                             "lat5", "lon5",
                             "lat6", "lon6",
                             "lat7", "lon7",
                             "lat8", "lon8",
                             "lat9", "lon9",
                             "lat10", "lon10",
                             "lat11", "lon11"]

    df = pd.DataFrame(columns=columns)

    hex_list = list()
    h3_address = h3.geo_to_h3(0, 0, 1)
    addr = h3.geo_to_h3(-28.762920, -93.321079, 1)
    addr3 = h3.geo_to_h3(8.313001, 111.705998, 1)
    for i in range(0, 20):
        hex_list.append(list(h3.k_ring_distances(h3_address, 20)[i]))
        hex_list.append(list(h3.k_ring_distances(addr, 20)[i]))
        hex_list.append(list(h3.k_ring_distances(addr3, 20)[i]))

    hex_list = [item for sublist in hex_list for item in sublist]
    set_hex_list = set(hex_list)
    if len(set_hex_list) != 842:
        # something went wrong
        print("There are hexagons missing... only have: ", len(set_hex_list))
        return
    for hex in set_hex_list:
        # print(hex)
        coords = h3.h3_to_geo_boundary(hex, geo_json=True)
        polygon_type = get_type(len(coords))
        if polygon_type is None:
            print(len(coords))
            continue
        # print(coords)
        row = list()
        row.append(hex)
        row.append(polygon_type)
        for coord in coords:
            row.append(coord[1])  # lon
            row.append(coord[0])  # lat
        if polygon_type == "pent":
            # because pandas dataframes need the correct amount of columns
            row += ["", "", "", "", "", "", "", "", "", ""]
        elif polygon_type == "hex":
            row += ["", "", "", "", "", "", "", ""]
        elif polygon_type == "hept":
            row += ["", "", "", "", "", ""]
        elif polygon_type == "oct":
            row += ["", "", "", ""]
        # print(row)
        # print(len(row))

        df.loc[len(df)] = row
    # print(len(df.index))
    df.to_csv("../CSV/keygroups_2.csv", index=False, sep=';')


if __name__ == "__main__":
    generate_keygroups()
