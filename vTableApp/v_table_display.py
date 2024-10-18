import ipyvuetify as v
import pandas as pd

from lazyfilter.utils import HasValidDataframe


class TableDisplay(HasValidDataframe, v.Container):
    def __init__(self, dataframe, *, show_index=True):
        self.dataframe = dataframe
        self.table = v.DataTable(
            headers=self._get_headers(show_index=show_index),
            items=self._get_items(),
            v_model="selected",
            item_key="index",
            single_select=True,
            show_select=True,
            multi_sort=True,
            items_per_page=15,
            footer_props={
                "show-first-last-page": True,
                "items-per-page-options": [5, 10, 15, 25, 50, -1],
            },
        )
        v.Container.__init__(
            self,
            children=[
                self.table,
            ],
        )

    def _get_headers(self, *, show_index=True):
        headers = [
            {"text": column.replace("_", " ").capitalize(), "value": column}
            for column in self.dataframe
        ]
        if show_index:
            headers = [{"text": "Index", "value": "index"}] + headers
        return headers

    @property
    def current_index(self):
        pd.Index([item["index"] for item in self.table.items if item is not None])

    def _get_items(self, *, index=None):
        if index is None:
            index = self.dataframe.index
        return [
            {"index": idx, **item}
            for idx, item in zip(
                index, self.dataframe.loc[index].to_dict(orient="records")
            )
        ]

    def _set_items(self, *, index=None):
        self.table.items = self._get_items(index=index)
