import ipyvuetify as v
import traitlets


class Autocomplete(v.VuetifyTemplate):  # type: ignore
    selection = traitlets.Any().tag(sync=True)
    search = traitlets.Any().tag(sync=True)
    items = traitlets.List().tag(sync=True)
    chips = traitlets.Bool(default_value=True).tag(sync=True)
    multiple = traitlets.Bool(default_value=True).tag(sync=True)
    label = traitlets.Unicode().tag(sync=True)
    class_ = traitlets.Unicode().tag(sync=True)
    style_ = traitlets.Unicode().tag(sync=True)

    @traitlets.default("template")
    def _template(self):
        return """
<template>
  <v-autocomplete
    v-model.sync="selection"
    :class="class_"
    :style="style_"
    :search-input.sync="search"
    :items="items"
    :label="label"
    :multiple="multiple"
    :chips="chips"
    deletable-chips
    clearable
  >
    <template v-slot:no-data>
        <v-list-item>
          <v-list-item-title>
            No results matching <strong>{{ search }}</strong>.
          </v-list-item-title>
        </v-list-item>
      </template>
  </v-autocomplete>
</template>
        """
