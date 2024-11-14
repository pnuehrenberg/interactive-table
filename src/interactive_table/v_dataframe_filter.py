from contextlib import contextmanager

import lazyfilter
import pandas as pd
import traitlets

from .traitlet_utils import MutableDict
from .v_badge_toggle import BadgeToggle
from .v_menu import Menu
from .v_range_filter import RangeFilter
from .v_selection_filter import SelectionFilter


class _DataFrameFilter(traitlets.HasTraits, lazyfilter.DataFrameFilter):
    description = MutableDict()  # type: ignore

    def __init__(self, dataframe, callbacks=None, track_description=True):
        traitlets.HasTraits.__init__(self)
        self.dataframe = dataframe
        self.dependencies = {}
        self.track_description = track_description
        self.widgets = {}
        self.callbacks = callbacks

    def add(self, filter, *, dependencies=None):
        def callback(selection):
            self.update({filter.column: selection})

        super().add(filter, dependencies=dependencies)
        column_name = self.column_name(filter)
        if filter.selected_values is None:
            filter_widget = RangeFilter(
                values=filter.values,
                allow_quantile_range_filter=filter.column != pd.Index,
                callbacks=[callback],
                class_="px-5 pt-5 pb-1",
                style_="width: 300px",
            )
        else:
            filter_widget = SelectionFilter(
                values=filter.values,
                callbacks=[callback],
                class_="px-5 pt-5 pb-0",
                style_="width: 300px",
                label=f"Select {column_name}",
            )
        filter_menu = Menu(
            open_button="mdi-filter",
            open_button_icon=True,
            open_button_class="ml-n4 my-0",
            close_button="",
            confirm_button="",
            content=[filter_widget],
        )
        widget = BadgeToggle(
            content=filter_menu,
            on_deactivate_callbacks=[filter_widget.reset, filter.reset],
        )
        self.widgets[filter] = widget
        # describe filter, but temporarily deactivate callbacks for initial description
        callbacks = self.callbacks
        self.callbacks = None
        self.describe(filter)
        self.callbacks = callbacks

    def is_filtering(self, filter):
        if not filter.is_active:
            return False
        widget = self.widgets[filter].content.content[0]
        if filter.filter_type == "quantile_range" and filter.value == (0, 1):
            return False
        if filter.filter_type == "value_range" and filter.value == (
            widget.min,
            widget.max,
        ):
            return False
        if (
            filter.filter_type == "selected_values"
            and (value := filter.value) is not None
            and len(value) == 0
        ):
            return False
        return True

    def _set_active(self, filter):
        self.widgets[filter].active = self.is_filtering(filter)

    @contextmanager
    def block_callbacks(self):
        _callbacks = self.callbacks
        self.callbacks = None
        try:
            yield
        except Exception as e:
            raise e
        finally:
            self.callbacks = _callbacks

    @traitlets.observe("description", type="mutation")
    def _description_change(self, change):
        for key in change["new"]:
            column, _, options, value = change["new"][key]
            set_value = True
            if str(change["old"][key]) != "Undefined":
                set_value = value != change["old"][key][3]
            filter = self.get(column)
            widget = self.widgets[filter].content.content[0]
            widget.values = filter.values
            if set_value and filter.is_active and widget.value != value:
                widget.value = value
            elif not filter.is_active and widget.is_active:
                widget.reset()
            self._set_active(filter)
        filtered_dataframe = self.apply(track_description=False)
        if self.callbacks is None:
            return
        for callback in self.callbacks:
            callback(filtered_dataframe)


lazyfilter.lazy.DataFrameFilter = _DataFrameFilter
lazy_filter = lazyfilter.lazy.lazy_filter
