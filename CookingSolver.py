from NGUIdle import NGUIdle
import numpy as np
from scipy.signal import argrelextrema
import numpy_indexed as npi
import logging
import time


def wait_for_ui_update(update_ui_delay=50/1000):
    time.sleep(update_ui_delay)


def extract_individual_values_at_0(ngu, nb_ingredients, nb_value_per_ingredient):
    print("Iterate one ingredient at a time while the rest is set to 0")
    data = np.zeros((nb_ingredients, nb_value_per_ingredient))
    for i in range(nb_ingredients):
        for value in range(nb_value_per_ingredient):
            ngu.cooking.set_ingredient_value(i, value)
            wait_for_ui_update()
            data[i][value] = ngu.cooking.get_meal_efficiency()[0]
        ngu.cooking.set_ingredient_value(i, 0)
    return data


def find_best_in_pair(ngu, nb_value_per_ingredient, peaks, ing1, ing2):
    peaks_ingredient = peaks[1, peaks[0, :] == ing1]
    best_pairs = []
    for idx1 in range(len(peaks_ingredient)):
        value1 = peaks_ingredient[idx1]
        ngu.cooking.set_ingredient_value(ing1, value1)
        for value2_ in range(nb_value_per_ingredient):
            value2 = value2_ if ((idx1 % 2) == 0) else nb_value_per_ingredient - value2_ - 1
            ngu.cooking.set_ingredient_value(ing2, value2)
            wait_for_ui_update()
            eff = ngu.cooking.get_meal_efficiency()[0]
            best_pairs.append(((value1, value2), eff))
            if (eff == 100):
                break
        if (eff == 100):
            break
    best_pair = max(best_pairs, key=lambda x: x[1])
    ngu.cooking.set_ingredient_value(ing1, best_pair[0][0])
    ngu.cooking.set_ingredient_value(ing2, best_pair[0][1])
    print(f"Found ingredients ({ing1} : {best_pair[0][0]}), ({ing2} : {best_pair[0][1]}) with %{best_pair[1]} efficiency")   # TODO: complete


def find_best_single(ngu, peaks, ing1):
    peaks_ingredient = peaks[1, peaks[0, :] == ing1]
    best_values = []
    for value1 in peaks_ingredient:
        ngu.cooking.set_ingredient_value(ing1, value1)
        wait_for_ui_update()
        eff = ngu.cooking.get_meal_efficiency()[0]
        best_values.append((value1, eff))
        if (eff == 100):
            break
    best_value = max(best_values, key=lambda x: x[1])
    ngu.cooking.set_ingredient_value(ing1, best_value[0])
    print(f"Found ingredient ing {ing1} : {best_value[0]} with %{best_value[1]} efficiency")


def best_solution_found(ngu: NGUIdle):
    return ngu.cooking.get_meal_efficiency()[0] == 100


def solve_cooking(ngu: NGUIdle):
    ngu.select_menu(ngu.Menus.Cooking)

    print("Reset ingredients to 0")
    ngu.cooking.reset_to_0()

    # data structure
    nb_ingredients = ngu.cooking.get_nb_ingredients()
    nb_value_per_ingredient = ngu.cooking.nb_value_per_ingredient

    data_file = "data.npy"
    try:
        data = np.load(data_file)
        print("WARNING: Loading pre-cached data")
    except OSError:
        data = extract_individual_values_at_0(ngu, nb_ingredients, nb_value_per_ingredient)
        # Uncomment the next line to skip the previous iteration
        # np.save(data_file, data)

    # print(data)

    print("Find duplicated ingredients")
    group: npi.GroupBy = npi.group_by(data)
    index_group = group.split(np.arange(data.shape[0]))
    index_group = sorted(index_group, key=lambda x: x[0])
    print(f"pairs and singles: {index_group}")

    print("Find all peaks")
    # include the edge (this adds one columns on each side)
    data_ = np.pad(data, ((0, 0), (1, 1)), mode='reflect')
    peaks = np.array(argrelextrema(data_, np.greater, axis=1))
    # subtract additional column index
    peaks[1, :] -= 1

    print("Identify all best values for each pair")
    pairs = [x for x in index_group if len(x) == 2]
    for ing1, ing2 in pairs:    # iterate all pairs
        find_best_in_pair(ngu, nb_value_per_ingredient, peaks, ing1, ing2)

        if (best_solution_found(ngu)):
            return True

    print("Identify all best values for unmatched ingredients")
    singles = [x for x in index_group if len(x) == 1]
    for ing1, in singles:
        find_best_single(ngu, peaks, ing1)

        if (best_solution_found(ngu)):
            return True

    if (best_solution_found(ngu)):
        return True
    else:
        print("Still not have found the perfect solution")

        print("Revision on pairs")
        for ing1, ing2 in pairs:    # iterate all pairs
            # set both ingredient to 20
            ngu.cooking.set_ingredient_value(ing1, nb_value_per_ingredient-1)
            ngu.cooking.set_ingredient_value(ing2, nb_value_per_ingredient-1)

            # find new peaks
            new_range = np.zeros((nb_value_per_ingredient))
            for value in reversed(range(nb_value_per_ingredient)):
                ngu.cooking.set_ingredient_value(ing1, value)
                wait_for_ui_update()
                new_range[value] = ngu.cooking.get_meal_efficiency()[0]
            new_range_ = np.pad(new_range, (1, 1), mode='reflect')

            new_ext = np.array(argrelextrema(new_range_, np.greater))
            # subtract additional column index
            new_ext[:] -= 1
            new_ext = np.pad(new_ext, ((1, 0), (0, 0)), constant_values=ing1)

            # has peaks changed?
            if not np.array_equal(peaks[:, peaks[0, :] == ing2], new_ext):
                print(f"Found new peaks with ingredient {ing1} and {ing2}")
                find_best_in_pair(ngu, nb_value_per_ingredient, new_ext, ing1, ing2)

                if (best_solution_found(ngu)):
                    return True

    return False


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    try:
        # Find NGU Idle
        ngu = NGUIdle()
    except Exception:
        print("NGUIdle not found")
        ngu = None

    if ngu:
        # Solve cooking
        result = solve_cooking(ngu)

        if (result):
            print("Found the perfect solution!")
        else:
            print("Have not found the perfect solution")
