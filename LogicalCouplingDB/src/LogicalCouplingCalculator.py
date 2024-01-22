import itertools
from operator import itemgetter

import os

class LogicalCouplingCalculator:

    def __init__(self):
        self.developers_coupling = []
        self.components_coupling = []

    def calculate(self, files_modified: list[str]) -> tuple[list[str],list[str],list[tuple[str, str]]]:
        components = [self.__root_calculator(file_path) for file_path in files_modified]
        combinations = list(itertools.combinations(list(set(components)), 2))
        combinations_sorted = sorted(combinations, key=itemgetter(0))
        return files_modified, components, combinations_sorted

        # for combination in combinations_sorted:
        #
        #
        #     to_find = f"C1:{combination[0]}!C2:{combination[1]}"
        #     cond = self.components_coupling[self.components_coupling['COMPONENTS'] == to_find]
        #     if cond.empty:
        #         self.components_coupling = self.components_coupling.append(
        #             {'COMPONENTS': to_find, 'COUPLING': 1}, ignore_index=True)
        #     else:
        #         self.components_coupling.loc[cond.index, 'COUPLING'] += 1
        #
        # self.loader.save()

    def __root_calculator(self, file_path:str) -> str:
        path = file_path.lstrip(os.sep)
        root = path[:path.index(os.sep)] if os.sep in path else path
        return root
