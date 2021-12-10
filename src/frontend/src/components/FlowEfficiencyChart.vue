<template>
  <div class="d-flex justify-center align-center">
    <div class="pa-2">
      <h3 class="pb-2">Flow Efficiency</h3>
      <p>
        Percentage of time where the flow item was active vs total time to
        complete
      </p>
    </div>
  </div>
  <div class="container mx-auto flex justify-center" id="efficiency" />
</template>

<script setup lang="ts">
import { defineProps, ref, onMounted, computed } from "vue";
import { LineChart } from "../d3charts/lineChart.js";
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
const url = `http://localhost:8181/metrics/efficiency?period=${props.period}&duration=${props.duration}&program_id=${props.programId}`;
function fetchMetricData() {
  let chartData = [];
  let flowCategories = ["feature", "defect", "debt", "risk"];
  axios.get(url).then((response) => {
    for (const bucket of response.data.buckets) {
      for (const [category, val] of Object.entries(bucket)) {
        let pushObject = { bucketStart: bucket.bucket_start };
        if (category != "bucket_start") {
          pushObject.flowCategory = category;
          pushObject.value = val;
          chartData.push(pushObject);
        }
      }
    }

    console.log(chartData);

    //Goal chartData to look like:
    // [
    //  {flowCategory: "defect", bucketStart: "100030223", value: 3},
    //  {flowCategory: "feature", bucketStart: "100030223", value: 2}
    //  ...
    // ]

    // zDomain: flowCategories,
    // colors: ["#80bc00", "#e05928", "#059abe", "#e2e43a"],
    const chart = LineChart(chartData, {
      x: (d) => d.bucketStart,
      y: (d) => d.value,
      z: (d) => d.flowCategory,
      yLabel: "↑ Efficiency (%)",
      height: 500, //TODO: make dynamic like distribution
      color: "steelblue", // TODO: change to match dashboard
    });

    const svg = d3.select("#efficiency").node().append(chart);
  });
}

onMounted(() => {
  fetchMetricData();
});
</script>
