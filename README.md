[![CircleCI](https://circleci.com/gh/coderepocenter/AxisUtilities.svg?style=svg)](https://circleci.com/gh/coderepocenter/AxisUtilities)
[![codecov](https://codecov.io/gh/coderepocenter/AxisUtilities/branch/master/graph/badge.svg)](https://codecov.io/gh/coderepocenter/AxisUtilities)



# What is `AxisUtilities`
`Axis Utilities` was originally developed to manages Time Axis and different operations related to time with the main 
focus on Earth & Atmospheric Science Community. For example, you might have a daily 3D spatially distributed temperature
and you want to calculate the monthly average of this data. This result in the same spatial coordinate, however, with
a different time axis/coordinate. 

However, similar operations could be performed on any one-dimensional axis. Let's say your data is distributed along the
z-coordinate in certain way, and now you want to average them in a different vertical distribution. Although, your 
source axis is not time anymore, the mathematical operation that is being performed is the same. For this reason, it was
decided to rename the package from [`TimeAxis`](https://github.com/maboualidev/TimeAxis) to 
[`AxisUtilities`](https://github.com/coderepocenter/AxisUtilities).

During the axis conversion (conversion from source axis to destination axis), for example computing the monthly mean
from the daily data, there are a lot of computations that needs to be done which does not involve the data itself. This
means that we could cache these computations and reuse them to achieve a better performance. As long as the source and
the destination axis have not changed, we could use the cached computation to perform the axis conversion. One of the
features that `AxisUtilities` provide is caching these computations and allowing you to reuse it to achieve better 
performance. The same concept is being used in other packages such as 
[`ESMF`](https://www.earthsystemcog.org/projects/esmf/), 
[`SCRIP`](https://github.com/SCRIP-Project/SCRIP), and 
[`2D and 3D Remapping`](https://www.mathworks.com/matlabcentral/fileexchange/41669-2d-and-3d-remapping). In those 
packages, the cached computation is referred as ***Remapping Weights***.

# How To Install?
## using pip
As usual, you could use `pip` installation as follows:

```shell script
pip install axisutilities
```

# How to use `AxisUtilities`?
The general procedure is:

1. Create a source axis, i.e. the axis that your original data is on,
2. Create a destination axis, i.e. the axis that you want to convert your data to,
3. Create a `AxisConverter` object by passing the source and destination axis you created previously,
4. Finally, convert your data from the source axis to the destination axis, using the `AxisConverter` object you created
in previous step.

You could repeat step (4) as many time as you want, as long as the source and destination axis are the same. The true
benefit of this approach is in the reuse of the same computations, a.k.a. ***remapping weights***.

For some examples refer to the following examples or the API documentations.

# Examples:
## Daily data averaged to weekly
**Step 1:** Create a source Axis

In this example, first we create a daily time-axis of length 14 days, i.e. we just have 14 data points
along the time axis:

```python
from_axis = DailyTimeAxisBuilder(
    start_date=date(2019, 1, 1),
    n_interval=14
).build()
```

**Step 2:** Create a destination Axis

Now we create a weekly time-axis of length 3, i.e. the time axis would have three elements with
span of 3 weeks:

```python
to_axis = WeeklyTimeAxisBuilder(
    start_date=date(2019, 1, 1),
    n_interval=3
).build()
```

**Step 3:** Create a `AxisConverter` object

now we create a time axis converter object, as follows:

```python
tc = AxisConverter(
    from_axis=from_axis, 
    to_axis=to_axis
)
```

**Step 4:** Converting data from source axis to destination axis

Now we can use `tc` to convert data from the `from_axis` to `to_axis`, as follows:

```python
to_data = tc.average(from_data)
```

the resulting `to_data` is the weekly average of the `from_data`. By default, we are assuming
that the first dimension is the time dimension. If the time dimension (source axis) is not the first dimension,
you could define it as follows:

```python
to_data = tc.average(from_data, time_dimension=n)
```

where `n` is the time dimension (or source axis if the axis you have created is not time).

**Repeating Step 4:** as many time as needed

If we have other data sources that are on the same source axis (in this case the same time axis), you could use the 
same `tc` or `AxisConverter` object that you created before to convert them to your new destination axis:

```python
to_data = tc.average(another_data_field)
```

**NOTE:** Please do note that only the 1D axis that you are converting from needs to be the same along all these 
different data sources. Their other dimensions could be completely different.

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

tc = TimeAxisConverter(from_axis=from_axis, to_axis=to_axis)

to_data = tc.average(from_data)
```

as you can see, the only difference is the construction og the `to_axis`. In this example,
we are building a rolling time axis that starts on `Jan. 1st, 2019` and ends on `Jan. 15th, 2019`
with a window size of `7`. Since the base time delta, if not provided, is one day, our window is
one week (`7 * 1 day`). However, this is a rolling time axis, meaning that the next element on 
time axis is shifted only one day. Yes, the intervals in the time-axis are overlapping each other.

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

tc = TimeAxisConverter(from_axis=from_axis, to_axis=to_axis)
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





