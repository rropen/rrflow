<template>
  <div class="d-flex justify-center align-center">
    <div class="pa-2">
      <h3 class="pb-2">Flow Velocity</h3>
      <p>Number of Flow Items completed in a period of time</p>
    </div>
  </div>
  <div class="container mx-auto flex justify-center" id="velocity" />
</template>

<script setup lang="ts">
import { defineProps, ref, onMounted, computed } from "vue";
import { BarChart } from "../d3charts/horizontalBar.js";
import axios from "axios";
import * as d3 from "d3";

const props = defineProps({
  programId: {
    type: String,
    required: true,
  },
  period: {
    type: String,
    required: true,
    default: "Month",
  },
  duration: {
    type: String,
    required: true,
    default: "Month",
  },
});

//--------------------------------------------------------------------------
//                   CALLING RRFLOW API AND CLEANING DATA
//--------------------------------------------------------------------------
const url = `http://localhost:8181/metrics/velocity?period=${props.period}&duration=${props.duration}&program_id=${props.programId}`;
function fetchMetricData() {
  let chartData = [];
  axios.get(url).then((response) => {
    for (const [category, val] of Object.entries(response.data.buckets[0])) {
      if (category != "bucket_start") {
        chartData.push({ flowCategory: category, value: val });
      }
    }

    const chart = BarChart(chartData, {
      x: (d) => d.value,
      y: (d) => d.flowCategory,
      marginLeft: 60,
      marginRight: 60,
      yDomain: d3.groupSort(
        chartData,
        ([d]) => -d.value,
        (d) => d.flowCategory
      ), // sort by descending frequency
      xLabel: `${response.data.units} →`,
      color: "steelblue",
    });

    const svg = d3.select("#velocity").node().append(chart);
  });
}

onMounted(() => {
  fetchMetricData();
});
</script>
