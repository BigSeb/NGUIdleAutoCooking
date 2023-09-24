from NGUIdle import NGUIdle
import numpy as np
from scipy.signal import argrelextrema
import numpy_indexed as npi
import logging


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
    except OSError:
        print("Iterate one ingredient at a time while the rest is set to 0")
        data = np.zeros((nb_ingredients, nb_value_per_ingredient))
        for i in range(nb_ingredients):
            for value in range(nb_value_per_ingredient):
                ngu.cooking.set_ingredient_value(i, value)
                data[i][value] = ngu.cooking.get_meal_efficiency()[0]
            ngu.cooking.set_ingredient_value(i, 0)
        # Uncomment the next line to skip the previous iteration
        # np.save(data_file, data)

    # print(data)

    print("Find duplicated ingredients")
    group: npi.GroupBy = npi.group_by(data)
    index_group = group.split(np.arange(data.shape[0]))
    index_group = sorted(index_group, key=lambda x: x[0])
    print(f"pairs and singles: {index_group}")

    print("Find all local extrema")
    # include the edge (this adds one columns on each side)
    data_ = np.pad(data, ((0, 0), (1, 1)), mode='reflect')
    e = np.array(argrelextrema(data_, np.greater, axis=1))
    # subtract additional column index
    e[1, :] -= 1

    print("Identify all best values for each pair")
    pairs = [x for x in index_group if len(x) == 2]
    for ing1, ing2 in pairs:    # iterate all pairs
        extremas = e[1, e[0, :] == ing1]
        best_pairs = []
        for value1 in extremas:
            ngu.cooking.set_ingredient_value(ing1, value1)
            for value2 in range(nb_value_per_ingredient):
                ngu.cooking.set_ingredient_value(ing2, value2)
                eff = ngu.cooking.get_meal_efficiency()[0]
                best_pairs.append(((value1, value2), eff))
        best_pair = max(best_pairs, key=lambda x: x[1])
        ngu.cooking.set_ingredient_value(ing1, best_pair[0][0])
        ngu.cooking.set_ingredient_value(ing2, best_pair[0][1])
        print(f"Found ingredients ing {ing1} : {best_pair[0][0]}, ing {ing2} : {best_pair[0][1]} with %{best_pair[1]} efficiency")

    print("Identify all best values for unmatched ingredients")
    singles = [x for x in index_group if len(x) == 1]
    for ing1, in singles:
        extremas = e[1, e[0, :] == ing1]
        best_values = []
        for value1 in extremas:
            ngu.cooking.set_ingredient_value(ing1, value1)
            eff = ngu.cooking.get_meal_efficiency()[0]
            best_values.append((value1, eff))
        best_value = max(best_values, key=lambda x: x[1])
        ngu.cooking.set_ingredient_value(ing1, best_value[0])
        print(f"Found ingredient ing {ing1} : {best_value[0]} with %{best_value[1]} efficiency")

    if ngu.cooking.get_meal_efficiency()[0] == 100:
        print("Found the perfect solution!")
    else:
        print("Still not have found the perfect solution")
        pass    # TODO: complete


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
        solve_cooking(ngu)

