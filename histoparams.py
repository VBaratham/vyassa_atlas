ismultiple = lambda x, y: (float(x)/y).is_integer()

mjj_binsize = 15
mjj_max = 3990  # Full range is 0 to this
# mjj_fit_range = (990, 1800)
mjj_fit_range = (1020, 1800)

assert ismultiple(mjj_max, mjj_binsize)
assert ismultiple(mjj_fit_range[0], mjj_binsize)
assert ismultiple(mjj_fit_range[1], mjj_binsize)

mj_binsize = 2
mj_max = 200  # Full range is 0 to this
mj_fit_range = (36, 72)
# mj_fit_range = (40, 80)

assert ismultiple(mj_max, mj_binsize)
assert ismultiple(mj_fit_range[0], mj_binsize)
assert ismultiple(mj_fit_range[1], mj_binsize)

