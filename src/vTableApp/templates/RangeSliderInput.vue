<template v-model:min="min" v-model:max="max">
    <div :class="class_" :style="style_">
        <v-range-slider
            hide-details
            :step="step"
            :min="min_rounded"
            :max="max_rounded"
            v-model="temp_range"
        />
        <div class="d-inline-flex align-start" style="width: 100%">
            <jupyter-widget :widget="lower" />
            <jupyter-widget :widget="upper" />
        </div>
    </div>
</template>

<script>
export default {
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
        },
    },
};
</script>
