import numpy as np
import scipy as sp
from scipy.optimize import linear_sum_assignment
# c = np.array((
#         [2, 3, 3],
#         [3, 2, 3],
#         [3, 3, 2],
#     ))
c = np.array((
    [9, 7],
    [6, 6]
))
row_ind, col_ind = linear_sum_assignment(c)
print(row_ind, col_ind)
print(c[row_ind, col_ind].sum())
