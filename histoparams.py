isinteger = lambda num: isinstance(num, (int, long))

mjj_binsize = 15
mjj_max = 3990
mjj_fit_range = (795, 1800)

assert isinteger(mjj_max/mjj_binsize)
assert isinteger(mjj_fit_range[0]/mjj_binsize)
assert isinteger(mjj_fit_range[1]/mjj_binsize)

mj_binsize = 2
mj_max = 200
mj_fit_range = (36, 72)

assert isinteger(mj_max/mj_binsize)
assert isinteger(mj_fit_range[0]/mj_binsize)
assert isinteger(mj_fit_range[1]/mj_binsize)

