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
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import FlowVelocityChart from "../components/FlowVelocityChart.vue";
import FlowTimeChart from "../components/FlowTimeChart.vue";
import FlowLoadChart from "../components/FlowLoadChart.vue";

const selectedProgramId = ref("61ad63a933d01399768faa93");
const selectedPeriod = ref("Month");
const selectedDuration = ref("Month");
</script>
