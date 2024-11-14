"""
Refer to spectate documentation.
https://python-spectate.readthedocs.io/en/latest/usage/spectate-in-traitlets.html
"""

from spectate import mvc
from traitlets import TraitType


class Mutable(TraitType):
    """A base class for mutable traits using Spectate"""

    # Overwrite this in a subclass.
    _model_type = None

    # The event type observers must track to spectate changes to the model
    _event_type = "mutation"

    # You can dissallow attribute assignment to avoid discontinuities in the
    # knowledge observers have about the state of the model. Removing the line below
    # will enable attribute assignment and require observers to track 'change'
    # events as well as 'mutation' events in to avoid such discontinuities.
    __set__ = None  # type: ignore

    def default(self, obj=None):
        """Create the initial model instance

        The value returned here will be mutated by users of the HasTraits object
        it is assigned to. The resulting events will be tracked in the ``callback``
        defined below and distributed to event observers.
        """
        if self._model_type is None:
            raise NotImplementedError("Overwrite _model_type in a subclass.")
        model = self._model_type()

        @mvc.view(model)
        def callback(model, events):
            obj.notify_change(
                dict(
                    self._make_change(model, events),
                    name=self.name,
                    type=self._event_type,
                )
            )

        return model

    def _make_change(self, model, events):
        """Construct a dictionary describing the change"""
        raise NotImplementedError()


class MutableDict(Mutable):
    """A mutable dictionary trait"""

    _model_type = mvc.Dict

    def _make_change(self, model, events):
        old, new = {}, {}
        for e in events:
            old[e["key"]] = e["old"]
            new[e["key"]] = e["new"]
        return {"value": model, "old": old, "new": new}
