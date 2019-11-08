[![CircleCI](https://circleci.com/gh/maboualidev/TimeAxis.svg?style=svg)](https://circleci.com/gh/maboualidev/TimeAxis)
[![codecov](https://codecov.io/gh/maboualidev/TimeAxis/branch/master/graph/badge.svg)](https://codecov.io/gh/maboualidev/TimeAxis)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3530859.svg)](https://doi.org/10.5281/zenodo.3530859)



# TimeAxis
Manages Time Axis and different operations related to time. Main focus is on Earth Science Data.
The main goal of this package is to provide a unified mechanism to convert/transform date from 
time axis to another. For example, if your original data set is on a daily basis, and you want 
to convert it to weekly average, `TimeAxis` package would be handy. This package follows the
same concept as in ESMF and SCRIPS. Although these two packages are for spatial coordinate
interpolation, `TimeAxis`, obviously, deals with the time dimension of the data. It calculates
a weight matrix stored as sparse matrix. Once you have the weights, any data field could be
converted from the original time axis to the provided destination time axis.

# How To Install
## using pip
as usual, you could use `pip` installation as follows:

```shell script
pip install timeaxis
```

# Examples:
## Daily data averaged to weekly
In this example, first we create a daily time-axis of length 14 days, i.e. we just have 14 data points
along the time axis:

```python
from_axis = DailyTimeAxisBuilder(
    start_date=date(2019, 1, 1),
    n_interval=14
).build()
```

Now we create a weekly time-axis of length 3, i.e. the time axis would have three elements with
span of 3 weeks:

```python
to_axis = WeeklyTimeAxisBuilder(
    start_date=date(2019, 1, 1),
    n_interval=3
).build()
```

now we create a time axis converter object, as follows:

```python
tc = TimeAxisConverter(
    from_time_axis=from_axis, 
    to_time_axis=to_axis
)
```

Now we can use `tc` to convert data from the `from_axis` to `to_axis`, as follows:

```python
to_data = tc.average(from_data)
```

the resulting `to_data` is the weekly average of the `from_data`. By default, we are assuming
that the first dimension is the time dimension. If the time dimension is not the first dimension,
you could define it as the following:

```python
to_data = tc.average(from_data, time_dimension=n)
```

where `n` is the time dimension.

# Rolling/moving weekly avarage
You could easily calculate a rolling or moving average of your data. Here is an example:

```python
from_axis = DailyTimeAxisBuilder(
    start_date=date(2019, 1, 1),
    n_interval=14
).build()

to_axis = RollingWindowTimeAxisBuilder(
    start_date=date(2019, 1, 1),
    end_date=date(2019, 1, 15),
    window_size=7
).build()

tc = TimeAxisConverter(from_time_axis=from_axis, to_time_axis=to_axis)

to_data = tc.average(from_data)
```

as you can see, the only difference is the construction og the `to_axis`. In this example,
we are building a rolling time axis that starts on `Jan. 1st, 2019` and ends on `Jan. 15th, 2019`
with a window size of `7`. Since the base time delta, if not provided, is one day, our window is
one week (`7 * 1day`). However, this is a rolling time axis, meaning that the next element on 
time axis is shifted only one day. Yes, the intervals in the time-axis overlap each other.

## Daily Averaged to Monthly

```python
# Daily time axis spanning ten years.
from_axis = DailyTimeAxisBuilder(
    start_date=date(2010, 1, 1),
    end_date=date(2020, 1, 1)
).build()

# Monthly Time Axis spanning 10 years.
to_axis = MonthlyTimeAxisBuilder(
    start_year=2010,
    end_year=2019,
).build()

tc = TimeAxisConverter(from_time_axis=from_axis, to_time_axis=to_axis)
monthly_avg = tc.average(daily_data)
```

if you do not provide any month, the start month is assumed to be the January and the end month is assumed to be
the December. If you want to control that you could pass the `start_month` and/or `end_month` to change this
behavior:

```python
to_axis = MonthlyTimeAxisBuilder(
    start_year=2010,
    start_monnth=4,
    end_year=2019,
    end_month=10
).build()
```

# Authors:
- Abouali, Mohammad (maboualidev@gmail.com; mabouali@ucar.edu)
- Banihirwe, Anderson (abanihi@ucar.edu)
- Long, Matthew (mclong@ucar.edu)





