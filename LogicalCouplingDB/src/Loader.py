# import pandas
#
# COMPONENTS_COUPLING_FILE = "data/components_coupling.csv"
# DEVELOPERS_COMPONENTS_FILE = "data/developers_coupling.csv"
#
#
# class Loader:
#     def __init__(self, branch_name: str, repo_name: str):
#         try:
#             self.components_coupling = pandas.read_csv(COMPONENTS_COUPLING_FILE)
#         except:
#             self.components_coupling = {}
#         try:
#             self.developers_coupling = pandas.read_csv(DEVELOPERS_COMPONENTS_FILE)
#         except:
#             self.developers_coupling = {}
#
#     def get_components_coupling(self):
#         return self.components_coupling
#
#     def get_developers_coupling(self):
#         return self.developers_coupling
#
#     def save(self):
#
#         if isinstance(self.developers_coupling, pandas.DataFrame):
#             self.developers_coupling.to_csv(DEVELOPERS_COMPONENTS_FILE, index=False)
#         else:
#             developers_coupling = pandas.DataFrame(self.developers_coupling)
#             developers_coupling.to_csv(DEVELOPERS_COMPONENTS_FILE, index=False)
#
#         if isinstance(self.components_coupling, pandas.DataFrame):
#             self.components_coupling.to_csv(COMPONENTS_COUPLING_FILE, index=False)
#         else:
#             components_coupling = pandas.DataFrame(self.components_coupling)
#             components_coupling.to_csv(COMPONENTS_COUPLING_FILE, index=False)
