import numpy as np
import pandas as pd
from typing import Union
from geopy.distance import geodesic

from config import latitude_lims, longitude_lims


def calculate_distance(a: Union[pd.Series, list, tuple], b: Union[pd.Series, list, tuple]) -> float:
    """
    Calculates distance of two points based on their coordinates
    Parameters
    ----------
    a : pd.Series, list, tuple - point A
    b : pd.Series, list, tuple - point B

    Returns
    -------
    distance : float - distance in kilometers
    """
    coords_1 = tuple(a)
    coords_2 = tuple(b)

    return geodesic(coords_1, coords_2).km


def find_closest_location(point_coordinates: Union[list, tuple], df_locations: pd.DataFrame,
                          proximity_level: float = 0.05):
    """
    For a given point find closest location from df with locations.

    Parameters
    ----------
    point_coordinates : list, tuple - (lat, lng) of the reference point
    df_locations : pd.DataFrame - location which are to be searched
    proximity_level : how many degrees around are to be searched

    Returns
    -------
    (lat, lng) of the closes point in df with locations
    """
    lat = point_coordinates[0]
    lng = point_coordinates[1]

    very_close_locations_df = (df_locations[
        df_locations["latitude"].between(lat - proximity_level, lat + proximity_level)
        & df_locations["longitude"].between(lng - proximity_level, lng + proximity_level)])

    very_close_locations_df["distance_to_point"] = pd.Series()
    if len(very_close_locations_df) == 0:
        return None

    for i, point in very_close_locations_df.iterrows():
        distance = calculate_distance(point_coordinates, (point["latitude"], point["longitude"]))
        very_close_locations_df["distance_to_point"].loc[i] = distance

    idx_min = very_close_locations_df.distance_to_point.idxmin()
    return (very_close_locations_df["latitude"].loc[idx_min],
            very_close_locations_df["longitude"].loc[idx_min])


def find_optimal_grid_points(all_locations_latitudes: list, all_locations_longitudes: list,
                             cities_df: pd.DataFrame):
    """
    Returns list of tuples with points which will be used as (lat, lng) grid for measurements.
    The returned points must be elements of the actual locations list

    Parameters
    ----------
    all_locations_latitudes : list - latitudes of the sensors
    all_locations_longitudes : list - longitudes of the sensors
    cities_df

    Returns
    -------
    List of tuples with coordinates
    """
    all_locations_df = pd.DataFrame({"latitude": all_locations_latitudes,
                                     "longitude": all_locations_longitudes})

    n_of_grid_elements = 25
    far_proximity = 0.8
    close_proximity = 0.05
    n_of_grid_points_expected = 450

    x = np.linspace(longitude_lims[0], longitude_lims[1], n_of_grid_elements)
    y = np.linspace(latitude_lims[0], latitude_lims[1], n_of_grid_elements)

    grid = []
    for lat in y:
        for lng in x:
            close_locations_df = all_locations_df[
                all_locations_df["latitude"].between(lat - far_proximity, lat + far_proximity)
                & all_locations_df["longitude"].between(lng - far_proximity, lng + far_proximity)]

            distances_to_close_locations = close_locations_df.apply(calculate_distance,
                                                                    args=((lat, lng),), axis=1)
            if len(distances_to_close_locations) > 0:
                argmin = np.argmin(distances_to_close_locations)
                closest_point_latitude = close_locations_df["latitude"].iloc[argmin]
                closest_point_longitude = close_locations_df["longitude"].iloc[argmin]

                grid_item = (closest_point_latitude, closest_point_longitude)

                if grid_item not in grid:
                    grid.append(grid_item)

    grid = list(set(grid))

    n_of_missing_points = n_of_grid_points_expected - len(grid)
    n_of_actually_added_points = 0

    for i, city in cities_df.iterrows():
        if n_of_actually_added_points >= n_of_missing_points:
            break

        closest_location_to_given_city = find_closest_location(
            (city["latitude"], city["longitude"]), all_locations_df, close_proximity)

        if (closest_location_to_given_city is not None
                and closest_location_to_given_city not in grid):
            grid.append(closest_location_to_given_city)
            n_of_actually_added_points += 1

    return grid
