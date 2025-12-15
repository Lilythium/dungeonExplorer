from csv import reader


def import_csv_layout(path):
    """
    takes path to csv, returns an 2D array of values
    """
    terrain_map = []
    with open(path) as map:
        level = reader(map, delimiter=',')
        for row in level:
            terrain_map.append(list(row))
        return terrain_map
