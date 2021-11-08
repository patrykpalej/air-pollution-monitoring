import numpy as np
import pandas as pd
from typing import Union
from geopy.distance import geodesic

from config import latitude_lims, longitude_lims


def transform_azimuth_to_xy(azimuth_degrees):
    azimuth_radians = 2 * np.pi * azimuth_degrees / 360
    return np.sin(azimuth_radians), np.cos(azimuth_radians)


def transform_xy_to_azimuth(x, y):
    return ((np.arctan2(x, y) * 360/(2*np.pi)) + 360) % 360


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


def find_closest_installation(point_coordinates: Union[list, tuple], df_installations: pd.DataFrame,
                              proximity_level: float = 0.05):
    """
    For a given point find closest location from df with locations.

    Parameters
    ----------
    point_coordinates : list, tuple - (lat, lng) of the reference point
    df_installations : pd.DataFrame - location which are to be searched
    proximity_level : how many degrees around are to be searched

    Returns
    -------
    (lat, lng) of the closes point in df with locations
    """
    lat = point_coordinates[0]
    lng = point_coordinates[1]

    very_close_installations_df = (df_installations[
        df_installations["latitude"].between(lat - proximity_level, lat + proximity_level)
        & df_installations["longitude"].between(lng - proximity_level, lng + proximity_level)])

    very_close_installations_df.loc[:, "distance_to_point"] = pd.Series()
    if len(very_close_installations_df) == 0:
        return None

    for i, point in very_close_installations_df.iterrows():
        distance = calculate_distance(point_coordinates, (point["latitude"], point["longitude"]))
        very_close_installations_df["distance_to_point"].loc[i] = distance

    idx_min = very_close_installations_df.distance_to_point.idxmin()
    return very_close_installations_df.drop("distance_to_point", axis=1).loc[idx_min].to_dict()


def find_optimal_grid_points(all_installations_list, cities_df: pd.DataFrame):
    """
    Returns list of tuples with points which will be used as (lat, lng) grid for measurements.
    The returned points must be elements of the actual locations list

    Parameters
    ----------
    all_installations_list : list - list of all installations dicts
    cities_df : pd.DataFrame - df of all cities taken from db

    Returns
    -------
    List of dicts with coordinates and other parameters of installations such as id, city etc.
    """
    n_of_grid_elements = 25
    far_proximity = 0.8
    close_proximity = 0.05
    n_of_grid_points_expected = 600
    n_of_biggest_cities = 150

    all_installations_df = pd.DataFrame(all_installations_list)
    grid = []
    row_idx = None
    for row_idx, city in cities_df.iterrows():
        if len(grid) >= n_of_biggest_cities:
            break

        closest_location_to_given_city = find_closest_installation(
            (city["latitude"], city["longitude"]), all_installations_df, close_proximity)

        if (closest_location_to_given_city is not None
                and closest_location_to_given_city not in grid):
            grid.append(closest_location_to_given_city)

    n_of_biggest_cities_processed = row_idx

    x = np.linspace(longitude_lims[0], longitude_lims[1], n_of_grid_elements)
    y = np.linspace(latitude_lims[0], latitude_lims[1], n_of_grid_elements)

    for lat in y:
        for lng in x:
            close_installations_df = all_installations_df[
                all_installations_df["latitude"].between(lat - far_proximity, lat + far_proximity)
                & all_installations_df["longitude"].between(lng - far_proximity, lng + far_proximity)]

            distances_to_close_locations = \
                close_installations_df[["latitude", "longitude"]].apply(calculate_distance,
                                                                        args=((lat, lng),), axis=1)
            if len(distances_to_close_locations) > 0:
                argmin = np.argmin(distances_to_close_locations)
                grid_item = close_installations_df.iloc[argmin].to_dict()

                if grid_item not in grid:
                    grid.append(grid_item)

    n_of_missing_points = n_of_grid_points_expected - len(grid)
    n_of_actually_added_points = 0
    for i, city in cities_df.iloc[n_of_biggest_cities_processed:].iterrows():
        if n_of_actually_added_points >= n_of_missing_points:
            break

        closest_location_to_given_city = find_closest_installation(
            (city["latitude"], city["longitude"]), all_installations_df, close_proximity)

        if (closest_location_to_given_city is not None
                and closest_location_to_given_city not in grid):
            grid.append(closest_location_to_given_city)
            n_of_actually_added_points += 1

    return grid
