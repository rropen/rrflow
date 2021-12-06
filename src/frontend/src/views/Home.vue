<template>
  <div class="home">
    <FlowVelocityChart
      :programId="selectedProgramId"
      :period="selectedPeriod"
      :duration="selectedDuration"
    />
    <FlowTimeChart
      :programId="selectedProgramId"
      :period="selectedPeriod"
      :duration="selectedDuration"
    />
    <FlowLoadChart
      :programId="selectedProgramId"
      :period="selectedPeriod"
      :duration="selectedDuration"
    />
    <FlowDistributionChart
      :programId="selectedProgramId"
      :period="selectedPeriodDistro"
      :duration="selectedDurationDistro"
    />
  </div>
  <div>
    Div to give space at the bottom so i dont have to see the chart laying on
    bottom of screen
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import FlowVelocityChart from "../components/FlowVelocityChart.vue";
import FlowTimeChart from "../components/FlowTimeChart.vue";
import FlowLoadChart from "../components/FlowLoadChart.vue";
import FlowDistributionChart from "../components/FlowDistributionChart.vue";

const selectedProgramId = ref("61ad63a933d01399768faa93");
const selectedPeriod = ref("Month");
const selectedDuration = ref("Month");
const selectedPeriodDistro = ref("Week");
const selectedDurationDistro = ref("Month");
</script>
