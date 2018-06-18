#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) Joseph Areeda (2015)
#
# This file is part of GWpy.
#
# GWpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWpy.  If not, see <http://www.gnu.org/licenses/>.
#

"""The timeseries CLI product
"""

from .cliproduct import TimeDomainProduct
from ..plot import Plot
from ..plot.tex import label_to_latex

__author__ = 'Joseph Areeda <joseph.areeda@ligo.org>'


class TimeSeries(TimeDomainProduct):
    """Plot one or more time series
    """
    action = 'timeseries'

    def get_ylabel(self):
        """Text for y-axis label,  check if channel defines it
        """
        units = self.units
        if len(units) == 1 and str(units[0]) == '':  # dimensionless
            return ''
        if len(units) == 1 and self.usetex:
            return units[0].to_string('latex')
        elif len(units) == 1:
            return units[0].to_string()
        elif len(units) > 1:
            return 'Multiple units'
        return super(TimeSeries, self).get_ylabel()

    def get_suptitle(self):
        """Start of default super title, first channel is appended to it
        """
        return 'Time series: {0}'.format(self.chan_list[0])

    def get_title(self):
        suffix = super(TimeSeries, self).get_title()
        rates = {ts.sample_rate for ts in self.timeseries}
        fss = '({0})'.format('), ('.join(map(str, rates)))
        return ', '.join([
            'Fs: {0}'.format(fss),
            'duration: {0}'.format(self.duration),
            suffix,
        ])

    def make_plot(self):
        """Generate the plot from time series and arguments
        """
        plot = Plot(figsize=self.figsize, dpi=self.dpi)
        ax = plot.gca(xscale='auto-gps')

        for series in self.timeseries:
            label = series.channel.name
            if self.usetex:
                label = label_to_latex(label)
            ax.plot(series, label=label)

        return plot

    def scale_axes_from_data(self):
        """Restrict data limits for Y-axis based on what you can see
        """
        # get tight limits for X-axis
        if self.args.xmin is None:
            self.args.xmin = min(ts.xspan[0] for ts in self.timeseries)
        if self.args.xmax is None:
            self.args.xmax = max(ts.xspan[1] for ts in self.timeseries)

        # autoscale view for Y-axis
        cropped = [ts.crop(self.args.xmin, self.args.xmax) for
                   ts in self.timeseries]
        ymin = min(ts.value.min() for ts in cropped)
        ymax = max(ts.value.max() for ts in cropped)
        self.plot.gca().yaxis.set_data_interval(ymin, ymax, ignore=True)
        self.plot.gca().autoscale_view(scalex=False)
