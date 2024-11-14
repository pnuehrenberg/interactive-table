<template
  v-model:min="min"
  v-model:max="max"
  v-model:value="value"
  >
  <v-text-field
    type="number"
    :label="label"
    :readonly="readonly"
    :min="min_rounded"
    :max="max_rounded"
    :step="step"
    :class="class_"
    :style="style_"
    v-model="temp_value"
    :rules="[
      (v) => !(!v && v !== 0) || 'Input required',
      (v) => (v >= this.min && v <= this.max) || `Input must be between ${this.min} and ${this.max}`,
      (v) => (this.step != 1 || (v % 1 == 0 || v == this.min || v == this.max)) || `Input must be whole number, ${this.min} or ${this.max}.`
    ]"
    @change="enforce_range"
  />
</template>

<script>
export default {
  methods: {
    enforce_range() {
      if (this.temp_value < this.min) {
        this.temp_value = this.min;
        this.value = Number(this.min);
      } else if (this.temp_value > this.max) {
        this.temp_value = this.max;
        this.value = Number(this.max);
      } else if (this.step == 1) {
        this.value = Math.min(Math.max(Math.round(Number(this.temp_value)), this.min), this.max);
        this.temp_value = this.value;
      } else if (!this.error) {
        this.value = Number(this.temp_value);
      }
    },
  },
  computed: {
    min_rounded() {
      if (this.step == 0) {
        return this.min; 
      } else {
        return Math.floor(this.min / this.step) * this.step;
      }
    },
    max_rounded() {
      if (this.step == 0) {
        return this.max; 
      } else {
        return Math.ceil(this.max / this.step) * this.step;
      }
    }
  }
};
</script>