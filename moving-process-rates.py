from functools import partial

import pandas as pd

from datetime import datetime

from numpy import ndarray

from bokeh.io import curdoc
from bokeh.document import Document
from bokeh.plotting import figure
from bokeh.models import (ColumnDataSource, DateRangeSlider, RangeSlider, Select, CheckboxButtonGroup, CustomJS,
                          GlyphRenderer, Div, Span)
from bokeh.models.ranges import Range1d
from bokeh.models.layouts import Column, Row
from bokeh.models.formatters import NumeralTickFormatter
from bokeh.models.tools import HoverTool, CrosshairTool, PanTool, BoxZoomTool, SaveTool, ResetTool


class MovingVolumesPlot:
    """
    Pairs a Bokeh figure and a ColumnDataSource that can be updated to change the figure. The figure is the plot of
    moving referral volumes that are the denominator of the rate that referrals are seen in 30d across different window
    sizes.

    Methods:
         get_figure - Returns the Bokeh figure object associated with the plot
         get_source - Returns the Bokeh ColumnDataSource object associated with the line glyphs
         get_lines - Returns a list of Bokeh GlyphRenderer objects for the line glyphs
    """

    def __init__(self,
                 rolling_df: pd.DataFrame,
                 start_dt: datetime,
                 ct: CrosshairTool) -> None:
        data_df = rolling_df.loc[(rolling_df['Clinic'] == '*ALL*'),
                                 ['Date',
                                  'Moving 28d % Seen in 30d',
                                  'Moving 91d % Seen in 30d',
                                  'Moving 182d % Seen in 30d',
                                  'Moving 364d % Seen in 30d',
                                  'Moving 28d # Aged',
                                  'Moving 91d # Aged',
                                  'Moving 182d # Aged',
                                  'Moving 364d # Aged']].copy()
        data_df['28d Tooltip'] = data_df['Moving 28d % Seen in 30d'] * 100.0
        data_df['91d Tooltip'] = data_df['Moving 91d % Seen in 30d'] * 100.0
        data_df['182d Tooltip'] = data_df['Moving 182d % Seen in 30d'] * 100.0
        data_df['364d Tooltip'] = data_df['Moving 364d % Seen in 30d'] * 100.0
        self.cds = ColumnDataSource(data=data_df)

        referrals_x_range = Range1d(start_dt, AS_OF_DATE)

        ht = HoverTool(
            tooltips=[
                ('date', '@Date{%F}'),
                ('28d', '@{28d Tooltip}{%0.1f}% over @{Moving 28d # Aged}{#,##0}'),
                ('91d', '@{91d Tooltip}{%0.1f}% over @{Moving 91d # Aged}{#,##0}'),
                ('182d', '@{182d Tooltip}{%0.1f}% over @{Moving 182d # Aged}{#,##0}'),
                ('364d', '@{364d Tooltip}{%0.1f}% over @{Moving 364d # Aged}{#,##0}')
            ],

            formatters={
                '@Date': 'datetime',
                '@{28d Tooltip}': 'printf',
                '@{91d Tooltip}': 'printf',
                '@{182d Tooltip}': 'printf',
                '@{364d Tooltip}': 'printf'
            },

            mode='vline',
            line_policy='none',
            toggleable=False
        )

        self.ct = ct

        self.plot = figure(title=None,
                           output_backend='svg',
                           x_axis_type='datetime',
                           x_range=referrals_x_range,
                           toolbar_location='below',
                           tools=[PanTool(), BoxZoomTool(), SaveTool(), ResetTool()])

        self.plot.yaxis.formatter = NumeralTickFormatter(format='#,##0')
        self.plot.yaxis.axis_label = "Moving Volume"
        self.plot.yaxis.axis_label_text_font = "arial"
        self.plot.yaxis.axis_label_text_font_size = "12pt"
        self.plot.yaxis.axis_label_text_font_style = "normal"
        self.plot.yaxis.axis_label_text_color = "#434244"
        self.plot.yaxis.major_label_text_color = "#434244"
        self.plot.yaxis.major_label_text_font = "arial"
        self.plot.yaxis.major_label_text_font_size = "12pt"
        self.plot.min_border_left = 60

        self.plot.xaxis.major_label_text_font = "arial"
        self.plot.xaxis.major_label_text_font_size = "10pt"
        self.plot.xaxis.major_label_text_color = "#434244"

        self.lines = [self.plot.line(x='Date',
                                     y='Moving 28d # Aged',
                                     line_width=2,
                                     line_dash='dotted',
                                     line_color='gray',
                                     alpha=0.8,
                                     muted_alpha=0.2,
                                     source=self.cds),
                      self.plot.line(x='Date',
                                     y='Moving 91d # Aged',
                                     line_width=2,
                                     line_dash='dashed',
                                     line_color='red',
                                     alpha=0.8,
                                     muted_alpha=0.2,
                                     source=self.cds),
                      self.plot.line(x='Date',
                                     y='Moving 182d # Aged',
                                     line_width=2,
                                     line_dash='solid',
                                     line_color='blue',
                                     alpha=0.8,
                                     muted_alpha=0.2,
                                     source=self.cds),
                      self.plot.line(x='Date',
                                     y='Moving 364d # Aged',
                                     line_width=2,
                                     line_dash='solid',
                                     line_color='black',
                                     alpha=0.8,
                                     muted_alpha=0.2,
                                     source=self.cds)]

        self.plot.add_tools(ht)
        self.plot.add_tools(self.ct)
    # END __init__

    def get_figure(self) -> figure:
        """Returns the Bokeh figure object associated with the plot"""
        return self.plot

    def get_source(self) -> ColumnDataSource:
        """Returns the Bokeh ColumnDataSource object associated with the line glyphs"""
        return self.cds

    def get_lines(self) -> list[GlyphRenderer]:
        """Returns a list of Bokeh GlyphRenderer objects for the line glyphs"""
        return self.lines
    # END CLASS MovingVolumesPlot


class MovingRatesPlot:
    """
    Pairs a Bokeh figure and a ColumnDataSource that can be updated to change the figure. The figure is the plot of
    moving rates that referrals are seen in 30d across different window sizes.

    Methods:
         get_figure - Returns the Bokeh figure object associated with the plot
         get_source - Returns the Bokeh ColumnDataSource object associated with the line glyphs
         get_lines - Returns a list of Bokeh GlyphRenderer objects for the line glyphs
    """

    def __init__(self, rolling_df: pd.DataFrame, start_dt: datetime) -> None:
        data_df = rolling_df.loc[(rolling_df['Clinic'] == '*ALL*'),
                                 ['Date',
                                  'Moving 28d % Seen in 30d',
                                  'Moving 91d % Seen in 30d',
                                  'Moving 182d % Seen in 30d',
                                  'Moving 364d % Seen in 30d',
                                  'Moving 28d # Aged',
                                  'Moving 91d # Aged',
                                  'Moving 182d # Aged',
                                  'Moving 364d # Aged']].copy()
        data_df['28d Tooltip'] = data_df['Moving 28d % Seen in 30d'] * 100.0
        data_df['91d Tooltip'] = data_df['Moving 91d % Seen in 30d'] * 100.0
        data_df['182d Tooltip'] = data_df['Moving 182d % Seen in 30d'] * 100.0
        data_df['364d Tooltip'] = data_df['Moving 364d % Seen in 30d'] * 100.0
        self.cds = ColumnDataSource(data=data_df)

        referrals_x_range = Range1d(start_dt, AS_OF_DATE)
        referrals_y_range = Range1d(0.0, 1.0)

        ht = HoverTool(
            tooltips=[
                ('date', '@Date{%F}'),
                ('28d', '@{28d Tooltip}{%0.1f}% over @{Moving 28d # Aged}{#,##0}'),
                ('91d', '@{91d Tooltip}{%0.1f}% over @{Moving 91d # Aged}{#,##0}'),
                ('182d', '@{182d Tooltip}{%0.1f}% over @{Moving 182d # Aged}{#,##0}'),
                ('364d', '@{364d Tooltip}{%0.1f}% over @{Moving 364d # Aged}{#,##0}')
            ],

            formatters={
                '@Date': 'datetime',
                '@{28d Tooltip}': 'printf',
                '@{91d Tooltip}': 'printf',
                '@{182d Tooltip}': 'printf',
                '@{364d Tooltip}': 'printf'
            },

            mode='vline',
            line_policy='none',
            toggleable=False
        )

        height_overlay = Span(dimension="height", line_dash="solid", line_width=1, line_color='black')
        self.ct = CrosshairTool(overlay=height_overlay, toggleable=False)

        self.plot = figure(title='Referrals Seen in 30 Days - Moving Rates',
                           output_backend='svg',
                           x_axis_type='datetime',
                           x_range=referrals_x_range,
                           y_range=referrals_y_range,
                           toolbar_location='below',
                           tools=[PanTool(), BoxZoomTool(), SaveTool(), ResetTool()])

        self.plot.yaxis[0].ticker.desired_num_ticks = 10
        self.plot.yaxis.formatter = NumeralTickFormatter(format='0 %')
        self.plot.yaxis.axis_label = "% Seen in 30d"
        self.plot.yaxis.axis_label_text_font = "arial"
        self.plot.yaxis.axis_label_text_font_size = "12pt"
        self.plot.yaxis.axis_label_text_font_style = "normal"
        self.plot.yaxis.axis_label_text_color = "#434244"
        self.plot.yaxis.major_label_text_color = "#434244"
        self.plot.yaxis.major_label_text_font = "arial"
        self.plot.yaxis.major_label_text_font_size = "12pt"
        self.plot.min_border_left = 60

        self.plot.xaxis.major_label_text_font = "arial"
        self.plot.xaxis.major_label_text_font_size = "10pt"
        self.plot.xaxis.major_label_text_color = "#434244"

        self.plot.title.text_color = '#434244'
        self.plot.title.text_font = 'tahoma'
        self.plot.title.text_font_size = '14pt'

        self.lines = [self.plot.line(x='Date',
                                     y='Moving 28d % Seen in 30d',
                                     line_width=2,
                                     line_dash='dotted',
                                     line_color='gray',
                                     alpha=0.8,
                                     muted_alpha=0.2,
                                     legend_label='28d',
                                     source=self.cds),
                      self.plot.line(x='Date',
                                     y='Moving 91d % Seen in 30d',
                                     line_width=2,
                                     line_dash='dashed',
                                     line_color='red',
                                     alpha=0.8,
                                     muted_alpha=0.2,
                                     legend_label='91d',
                                     source=self.cds),
                      self.plot.line(x='Date',
                                     y='Moving 182d % Seen in 30d',
                                     line_width=2,
                                     line_dash='solid',
                                     line_color='blue',
                                     alpha=0.8,
                                     muted_alpha=0.2,
                                     legend_label='182d',
                                     source=self.cds),
                      self.plot.line(x='Date',
                                     y='Moving 364d % Seen in 30d',
                                     line_width=2,
                                     line_dash='solid',
                                     line_color='black',
                                     alpha=0.8,
                                     muted_alpha=0.2,
                                     legend_label='364d',
                                     source=self.cds)]

        self.plot.legend.location = 'bottom_left'
        self.plot.legend.click_policy = 'mute'

        self.plot.toolbar.logo = None

        self.plot.add_tools(ht)
        self.plot.add_tools(self.ct)
    # END __init__

    def get_figure(self) -> figure:
        """Returns the Bokeh figure object associated with the plot"""
        return self.plot

    def get_source(self) -> ColumnDataSource:
        """Returns the Bokeh ColumnDataSource object associated with the line glyphs"""
        return self.cds

    def get_shared_crosshair(self) -> CrosshairTool:
        """Returns the Bokeh model object associated with the crosshair tool"""
        return self.ct

    def get_lines(self) -> list[GlyphRenderer]:
        """Returns a list of Bokeh GlyphRenderer objects for the line glyphs"""
        return self.lines
# END CLASS MovingRatesPlot


class ClinicSlicer:
    """
    This class creates a Bokeh Select model with a drop-down list of clinic names and pairs a callback function
    with a ColumnDataSource that updates associated Bokeh models with a filtered data set.

    Methods:
        get_slicer_model - Returns the Bokeh model object associated with the slicer widget
    """

    def __init__(self, upper_cds: ColumnDataSource, lower_cds: ColumnDataSource, df: pd.DataFrame) -> None:
        self.upper_cds = upper_cds
        self.lower_cds = lower_cds
        self.df = df
        self.clinics = df['Clinic'].unique().tolist()[::1]
        self.clinic_select = Select(value='*ALL*', options=self.clinics)
        self.clinic_select.on_change("value", self._clinic_slicer_callback)

    def _clinic_slicer_callback(self, attr: str, old, new) -> None:
        """This function is assigned to Bokeh models as a callback and filters the data by clinic name."""
        idx = (self.df['Clinic'] == new)
        new_df = (self.df.loc[idx, ['Date',
                                    'Moving 28d % Seen in 30d',
                                    'Moving 91d % Seen in 30d',
                                    'Moving 182d % Seen in 30d',
                                    'Moving 364d % Seen in 30d',
                                    'Moving 28d # Aged',
                                    'Moving 91d # Aged',
                                    'Moving 182d # Aged',
                                    'Moving 364d # Aged']].copy())
        new_df['28d Tooltip'] = new_df['Moving 28d % Seen in 30d'] * 100.0
        new_df['91d Tooltip'] = new_df['Moving 91d % Seen in 30d'] * 100.0
        new_df['182d Tooltip'] = new_df['Moving 182d % Seen in 30d'] * 100.0
        new_df['364d Tooltip'] = new_df['Moving 364d % Seen in 30d'] * 100.0
        self.upper_cds.data = create_dict_like_bokeh_does(new_df)
        self.lower_cds.data = create_dict_like_bokeh_does(new_df)
    # END clinic_filter_callback

    def get_slicer_model(self) -> Select:
        """Returns the Bokeh model object associated with the slicer widget."""
        return self.clinic_select
# END CLASS DataFilterCallback


class ConnectedXDateRangeSlider:
    """
    This class creates a Bokeh DateRangeSlider model that updates the start and end of the x-axis range in the
    given figure using callbacks. This slider also connects to the x-axis model of the associated figure and updates
    the slider set points when the figure's x-axis range is changed by the interactive Bokeh tools.

    Methods:
        get_slider_model - Returns the Bokeh model object associated with the slider widget
    """
    def __init__(self,
                 title: str,
                 start: float,
                 end: float,
                 step: float,
                 value: tuple[float, float],
                 plots: list[figure]) -> None:
        self.slider = DateRangeSlider(title=title, start=start, end=end, step=step, value=value)
        self.plots = plots
        self.callbacks = []
        self.slider.on_change('value', self._update_plot_ranges_from_slider)
        for plot in self.plots:
            cb = partial(self._update_ranges_from_plot, plot=plot)
            self.callbacks.append(cb)
            plot.x_range.on_change('start', cb)
            plot.x_range.on_change('end', cb)
    # END __init__

    def _disable_callbacks(self, exception_plot: figure = None) -> None:
        """Disables all callbacks excepting the callbacks on the given plot."""
        self.slider.remove_on_change('value', self._update_plot_ranges_from_slider)
        for plot, cb in zip(self.plots, self.callbacks):
            if ~(plot == exception_plot):
                plot.x_range.remove_on_change('start', cb)
                plot.x_range.remove_on_change('end', cb)

    def _enable_callbacks(self, exception_plot: figure = None) -> None:
        """Re-enables all callbacks excepting the callbacks on the given plot."""
        self.slider.on_change('value', self._update_plot_ranges_from_slider)
        for plot, cb in zip(self.plots, self.callbacks):
            if ~(plot == exception_plot):
                plot.x_range.on_change('start', cb)
                plot.x_range.on_change('end', cb)

    def _update_ranges(self, new: tuple[float, float], exception_plot: figure = None) -> None:
        """Updates the ranges on all plots except the given plot with the given tuple of start, end values."""
        for plot in self.plots:
            if ~(plot == exception_plot):
                plot.x_range.start = new[0]
                plot.x_range.end = new[1]

    def _update_ranges_from_plot(self, attr, old, new, plot: figure) -> None:
        """Updates the start and end range values in the slider and the x-axes of connected plots from a given plot."""
        # Stop changes caused by this callback from reflecting as another callback
        self._disable_callbacks(plot)
        new_value = (plot.x_range.start, plot.x_range.end)
        self.slider.update(value=new_value)
        self._update_ranges(new_value, plot)
        self._enable_callbacks(plot)

    def _update_plot_ranges_from_slider(self, attr, old, new) -> None:
        """Updates the start and end range values in the x-axis of all plots using the values from the slider."""
        # Stop changes caused by this callback from reflecting as another callback
        self._disable_callbacks()
        self._update_ranges(new)
        self._enable_callbacks()

    def get_slider_model(self) -> DateRangeSlider:
        """Returns the Bokeh model object associated with the slider widget."""
        return self.slider
# END CLASS ConnectedXDateRangeSlider


class ConnectedYRangeSlider:
    """
    This class creates a Bokeh RangeSlider model that updates the start and end of the y-axis range in the
    given figure using callbacks. This slider also connects to the y-axis model of the associated figure and updates
    the slider set points when the figure's y-axis range is changed by the interactive Bokeh tools.

    Methods:
        get_slider_model - Returns the Bokeh model object associated with the slider widget
    """

    def __init__(self,
                 title: str,
                 start: float,
                 end: float,
                 step: float,
                 value: tuple[float, float],
                 format_str: str,
                 plot: figure) -> None:
        self.slider = RangeSlider(title=title, start=start, end=end, step=step, value=value, format=format_str)
        self.plot = plot
        self.slider.on_change('value', self._update_plot_range)
        self.plot.y_range.on_change('start', self._update_slider_start)
        self.plot.y_range.on_change('end', self._update_slider_end)
    # END __init__

    def _update_slider_start(self, attr, old, new):
        """Updates the start value in the range slider's value tuple with the given new value."""
        new_value = list(self.slider.value)
        new_value[0] = new
        new_value = tuple(new_value)
        self.slider.update(start=0.0, end=1.0, value=new_value)
    # END _update_slider_start

    def _update_slider_end(self, attr, old, new):
        """Updates the end value in the range slider's value tuple with the given new value."""
        new_value = list(self.slider.value)
        new_value[1] = new
        new_value = tuple(new_value)
        self.slider.update(start=0.0, end=1.0, value=new_value)
    # END _update_slider_end

    def _update_plot_range(self, attr, old, new):
        """Updates the plot figure's y-axis start and end values from the given new range tuple."""
        new_value = list(new)
        self.plot.y_range.start = new_value[0]
        self.plot.y_range.end = new_value[1]
    # END _update_plot_range

    def get_slider_model(self) -> RangeSlider:
        """Returns the Bokeh model object associated with the slider widget."""
        return self.slider
# END CLASS ConnectedYRangeSlider


DATE_COLUMNS = ['Date Referral Sent',
                'Date Referral Seen',
                'Date Patient Checked In',
                'Date Held',
                'Date Pending Reschedule',
                'Date Last Referral Update',
                'Date Similar Appt Scheduled',
                'Date Accepted',
                'Date Referral Written',
                'Date Referral Completed',
                'Date Referral Scheduled']

COLUMN_TYPES = {
    'Referral ID': 'string',
    'Source Location': 'string',
    'Provider Referred To': 'string',
    'Location Referred To': 'string',
    'Referral Priority': 'string',
    'Referral Status': 'string',
    'Patient ID': 'string',
    'Clinic': 'string',
    'Last Referral Update By': 'string',
    'Assigned Personnel': 'string',
    'Organization Referred To': 'string',
    'Reason for Hold': 'string',
    'Referral Sub-Status': 'string',
    'Date Referral Sent': 'object',
    'Date Referral Seen': 'object',
    'Date Patient Checked In': 'object',
    'Date Held': 'object',
    'Date Pending Reschedule': 'object',
    'Date Last Referral Update': 'object',
    'Date Similar Appt Scheduled': 'object',
    'Date Accepted': 'object',
    'Date Referral Written': 'object',
    'Date Referral Completed': 'object',
    'Date Referral Scheduled': 'object'}

DATA_FILE = 'referrals.csv'
AS_OF_DATE = datetime(2023, 3, 1)


def create_dict_like_bokeh_does(df: pd.DataFrame) -> dict[str, ndarray]:
    """Returns a dictionary of data from a DataFrame with columns as ndarrays and proper typecasting."""
    tmp_data = {c: v.values for c, v in df.items()}
    new_data = {}
    for k, v in tmp_data.items():
        new_data[k] = v
    return new_data
# END create_dict_like_bokeh_does


def load_data(file_path: str, columns: dict[str, str], date_columns: list[str]) -> pd.DataFrame:
    """
    Extracts referral data from a text file and returns a DataFrame.
    :param file_path: The path to the file with the referral data
    :param columns: The names and intended data types of each column in the file
    :param date_columns: The names of the columns to be typecast as datetime
    :return: A dataframe of referral data
    """
    df = pd.read_csv(file_path, header=0, dtype=columns)
    # This seems to work better than asking read_csv to convert datetime columns
    df[date_columns] = df[date_columns].apply(pd.to_datetime)
    return df
# END load_data


def get_measurement_dates(df: pd.DataFrame) -> tuple[datetime, datetime]:
    """Returns a tuple with the first and last measurement dates from the given DataFrame of referral data."""
    start_dt = min(df['Date Referral Sent +31d'])
    end_dt = max(df['Date Referral Sent +31d'])
    return start_dt, end_dt
# END get_measurement_dates


def create_calendar(start_dt: datetime, end_dt: datetime) -> pd.DataFrame:
    """Returns a DataFrame with all calendar dates across a given range of dates."""
    return pd.DataFrame({'Date': pd.date_range(start_dt, end_dt)})


def process_record_transforms(df: pd.DataFrame) -> None:
    """Adds columns of record specific measurements to the given DataFrame of referral data."""

    # Create an offset date when the referral reached 30 days of age
    df['Date Referral Sent +31d'] = df['Date Referral Sent'] + pd.Timedelta(days=31)
    df['As Of Date'] = AS_OF_DATE

    # Days until the referral tagged as seen or patient checked into clinic appointment
    df['Date Patient Seen or Checked In'] = df['Date Referral Seen']
    idx = df['Date Patient Seen or Checked In'].isna()
    df.loc[idx, 'Date Patient Seen or Checked In'] = df.loc[
        idx, 'Date Patient Checked In']
    df['Days until Patient Seen or Check In'] = (
            (df['Date Patient Seen or Checked In'] - df[
                'Date Referral Sent']) / pd.Timedelta(days=1))
    idx = df['Date Patient Seen or Checked In'].isna()
    df.loc[idx, 'Days until Patient Seen or Check In'] = (
            (df.loc[idx, 'As Of Date'] - df.loc[
                idx, 'Date Referral Sent']) / pd.Timedelta(days=1))

    # Create a convenience column to aggregate referrals that are sent and not
    # rejected, canceled, or closed without being seen
    idx = ((~df['Date Referral Sent'].isna())
           & (~df['Referral Status'].isin(['Rejected', 'Cancelled']))
           & (~df['Referral Status'].isin(['Closed', 'Completed']) | (
                ~df['Date Patient Seen or Checked In'].isna())))
    df['Referral Aged Yn'] = 0
    df.loc[idx, 'Referral Aged Yn'] = 1

    # Create a convenience column to aggregate referrals that seen or checked in to an
    # appointment at the same clinic
    idx = ~df['Date Patient Seen or Checked In'].isna()
    df['Referral Seen or Checked In Yn'] = 0
    df.loc[idx, 'Referral Seen or Checked In Yn'] = 1
# END process_record_transforms


def calculate_window_measures(df: pd.DataFrame, num_days: int) -> pd.DataFrame:
    """Helper function to add rolling measures to given DataFrame across a given window size in days."""
    window_name = f'{num_days}d'
    measure_prefix = f'Moving {num_days}d '

    measure_df = (
        df.groupby(['Clinic'])
        .rolling(window=window_name, on='Date')['# Aged'].sum()
        .rename(measure_prefix + '# Aged')
        .reset_index())
    result_df = pd.merge(df, measure_df, how='left', on=['Clinic', 'Date'])

    measure_df = (
        df.groupby(['Clinic'])
        .rolling(window=window_name, on='Date')['# Seen in 30d'].sum()
        .rename(measure_prefix + '# Seen in 30d')
        .reset_index())
    result_df = pd.merge(result_df, measure_df, how='left', on=['Clinic', 'Date'])

    result_df[measure_prefix + '% Seen in 30d'] = round(
            result_df[measure_prefix + '# Seen in 30d']
            / result_df[measure_prefix + '# Aged'], 3)

    return result_df
# END calculate_window_measures


def calculate_rolling_measures(referrals_df: pd.DataFrame) -> tuple[pd.DataFrame, datetime, datetime]:
    """Returns a DataFrame of rolling calendar window measures using the given DataFrame of referral data."""

    # Create a measurement calendar and apply the referrals data to the calendar on the date that each
    # referral reaches 30 days of age
    start_dt, end_dt = get_measurement_dates(referrals_df)
    calendar_df = create_calendar(start_dt, end_dt)
    source_df = pd.merge(calendar_df, referrals_df, how='left', left_on=['Date'], right_on=['Date Referral Sent +31d'])

    # Calculate count of referrals reaching 30 days of age on each calendar date
    rolling_df = calendar_df.copy()
    rolling_df['Clinic'] = '*ALL*'
    count_by_date_df = (
        source_df.groupby('Date')
        .agg({'Referral Aged Yn': 'sum'})
        .rename(columns={'Referral Aged Yn': '# Aged'}))
    rolling_df = pd.merge(rolling_df, count_by_date_df, how='left', on='Date')

    # Calculate count of referrals seen in 30 days by each calendar date
    # All referrals wait 30 days before being measured for consistency, even if they are seen sooner
    idx = (
        (source_df['Referral Aged Yn'] == 1)
        & (source_df['Referral Seen or Checked In Yn'] == 1)
        & (source_df['Days until Patient Seen or Check In'] < 31))
    count_by_date_df = (
        source_df.loc[idx].groupby('Date')
        .agg({'Referral Aged Yn': 'sum'})
        .rename(columns={'Referral Aged Yn': '# Seen in 30d'}))
    rolling_df = pd.merge(rolling_df, count_by_date_df, how='left', on='Date')

    # Calculate count of referrals reaching 30 days of age on each calendar date broken out by clinic
    count_by_date_df = (
        source_df.groupby(['Clinic', 'Date'])
        .agg({'Referral Aged Yn': 'sum'})
        .rename(columns={'Referral Aged Yn': '# Aged'})
        .reset_index())

    # Calculate count of referrals seen in 30 days by each calendar date broken out by clinic
    # All referrals wait 30 days before being measured for consistency, even if they are seen sooner
    idx = (
            (source_df['Referral Aged Yn'] == 1)
            & (source_df['Referral Seen or Checked In Yn'] == 1)
            & (source_df['Days until Patient Seen or Check In'] < 31))
    count_by_date_2_df = (
        source_df.loc[idx].groupby(['Clinic', 'Date'])
        .agg({'Referral Aged Yn': 'sum'})
        .rename(columns={'Referral Aged Yn': '# Seen in 30d'})
        .reset_index())
    count_by_date_df = pd.merge(count_by_date_df, count_by_date_2_df, how='left', on=['Clinic', 'Date'])

    # Merge daily counts by clinic with the daily counts across all clinics into one dataframe
    rolling_df = pd.merge(rolling_df,
                          count_by_date_df,
                          how='outer',
                          on=['Clinic', 'Date', '# Aged', '# Seen in 30d']).fillna(0)
    rolling_df['# Seen in 30d'] = rolling_df['# Seen in 30d'].astype(int)
    rolling_df.sort_values(['Clinic', 'Date'], axis=0, inplace=True, ignore_index=True)

    for days in [28, 91, 182, 364]:
        rolling_df = calculate_window_measures(rolling_df, days)

    return rolling_df, start_dt, end_dt
# END calculate_rolling_measures


def create_window_buttons(doc: Document,
                          upper_plot: MovingRatesPlot,
                          lower_plot: MovingVolumesPlot) -> CheckboxButtonGroup:
    """Returns a group of buttons to hide or show the lines for each moving window in box plots."""
    cb = CheckboxButtonGroup(labels=['28d', '91d', '182d', '364d'], active=[1, 3])
    callback_code = """
        for (let i = 0; i < upper.length; i++) {
            upper[i].visible = false;
            lower[i].visible = false;
        } 
        for (let i = 0; i < group.active.length; i++) {
            upper[group.active[i]].visible = true;
            lower[group.active[i]].visible = true;
        } 
    """
    cb.js_on_event("button_click", CustomJS(args=dict(group=cb,
                                                      upper=upper_plot.get_lines(),
                                                      lower=lower_plot.get_lines()), code=callback_code))
    doc.js_on_event("document_ready", CustomJS(args=dict(group=cb,
                                                         upper=upper_plot.get_lines(),
                                                         lower=lower_plot.get_lines()), code=callback_code))
    return cb
# END create_window_buttons


def link_line_mutes(upper_plot: MovingRatesPlot, lower_plot: MovingVolumesPlot) -> None:
    """Links the muted state of the lines in the moving rates plot and the moving volumes plot."""
    upper_plot_lines = upper_plot.get_lines()
    lower_plot_lines = lower_plot.get_lines()

    for line1, line2 in zip(upper_plot_lines, lower_plot_lines):
        cb = CustomJS(args=dict(line1=line1, line2=line2),
                      code="""
                        line2.muted = line1.muted
                      """)
        line1.js_on_change('muted', cb)


def create_range_sliders(upper_plot: figure,
                         lower_plot: figure) -> tuple[ConnectedXDateRangeSlider, ConnectedYRangeSlider]:
    """Returns X and Y axis sliders that are connected to the given plot."""
    x = ConnectedXDateRangeSlider(
        title='x-axis range',
        start=upper_plot.x_range.start,
        end=upper_plot.x_range.end,
        step=1,
        value=(upper_plot.x_range.start, upper_plot.x_range.end),
        plots=[upper_plot, lower_plot])

    y = ConnectedYRangeSlider(
        title='y-axis range',
        start=0.00,
        end=1.00,
        step=0.01,
        value=(0.00, 1.00),
        format_str='0 %',
        plot=upper_plot)

    return x, y
# END create_range_sliders


def add_layout(doc: Document,
               upper_plot: figure,
               lower_plot: figure,
               x: DateRangeSlider,
               y: RangeSlider,
               slicer: Select,
               cb: CheckboxButtonGroup) -> None:
    """Adds Bokeh models to a page layout in the application document."""
    slicer_title = Div(text='Select a clinic', margin=(40, 5, 5, 5))
    cb_title = Div(text='Show or hide window sizes in chart')
    spacer = Div(text=' ', margin=(20, 5, 5, 5))
    spacer2 = Div(text=' ', margin=(20, 5, 5, 5))
    note = Div(text='Click on items in the legend to mute their display')
    upper_plot.height = 375
    lower_plot.height = 200
    inputs = Column(slicer_title, slicer, cb_title, cb, spacer, x, y, spacer2, note)
    plots = Column(upper_plot, lower_plot)
    doc.add_root(Row(plots, inputs, width=800))
    doc.title = "Moving Process Rates"
# END add_layout


# TOP-LEVEL

print('loading referral data...')
referral_df = load_data(DATA_FILE, COLUMN_TYPES, DATE_COLUMNS)
print('processing record transforms...')
process_record_transforms(referral_df)
print('calculating rolling measures...')
rolling_measures_df, first_measure_dt, last_measure_dt = calculate_rolling_measures(referral_df)
print('adding Bokeh plots...')
rates_plot = MovingRatesPlot(rolling_measures_df, first_measure_dt)
volumes_plot = MovingVolumesPlot(rolling_measures_df, first_measure_dt, rates_plot.get_shared_crosshair())
x_range_slider, y_range_slider = create_range_sliders(rates_plot.get_figure(), volumes_plot.get_figure())
clinic_slicer = ClinicSlicer(rates_plot.get_source(), volumes_plot.get_source(), rolling_measures_df)
window_buttons = create_window_buttons(curdoc(), rates_plot, volumes_plot)
link_line_mutes(rates_plot, volumes_plot)
add_layout(curdoc(),
           rates_plot.get_figure(),
           volumes_plot.get_figure(),
           x_range_slider.get_slider_model(),
           y_range_slider.get_slider_model(),
           clinic_slicer.get_slicer_model(),
           window_buttons)
