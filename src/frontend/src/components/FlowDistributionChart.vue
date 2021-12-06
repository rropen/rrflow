<template>
  <div class="d-flex justify-center align-center">
    <div class="pa-2">
      <h3 class="pb-2">Flow Distribution</h3>
      <p>Distribution of Flow Items completed in that period</p>
    </div>
  </div>
  <div class="container mx-auto flex justify-center" id="distribution" />
</template>

<script setup lang="ts">
import { defineProps, ref, onMounted, computed } from "vue";
import { StackedBarChart } from "../d3charts/stackedBar.js";
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
const url = `http://localhost:8181/metrics/distribution?period=${props.period}&duration=${props.duration}&program_id=${props.programId}`;
function fetchMetricData() {
  let chartData = [];
  let flowCategories = ["feature", "defect", "debt", "risk"];
  axios.get(url).then((response) => {
    // TODO: make this dynamic for multiple buckets (not just data.buckets[0])
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

    // TODO: Make this chart vertical and convert date to readable format
    const chart = StackedBarChart(chartData, {
      x: (d) => d.value,
      y: (d) => d.bucketStart,
      z: (d) => d.flowCategory,
      marginLeft: 60,
      marginRight: 60,
      // yDomain: d3.groupSort(chartData, ([d]) => -d.bucketStart, (d) => d.flowCategory),
      // yDomain: (chartData.bucketStart),
      zDomain: flowCategories,
      colors: ["#80bc00", "#e05928", "#059abe", "#e2e43a"],
    });

    const svg = d3.select("#distribution").node().append(chart);
  });
}

onMounted(() => {
  fetchMetricData();
});
</script>
