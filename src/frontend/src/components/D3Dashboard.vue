<template>
  <div>
    <div>
      <div>
        <div cols="4" class="d-flex justify-center align-center">
          <div class="pa-2">
            <h3 class="pb-2">Flow Load</h3>
            <p>Number of Flow Items that are currently open</p>
          </div>
        </div>
        <div id="arc" />
        <div class="container mx-auto flex justify-center" id="hBar" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Vue } from "vue-class-component";
import { BarChart } from "../d3charts/horizontalBar.js";
import * as d3 from "d3";

const gdp = [
  { country: "USA", value: 20.5 },
  { country: "China", value: 13.4 },
  { country: "Germany", value: 4.0 },
  { country: "Japan", value: 4.9 },
  { country: "France", value: 2.8 },
];

const load = [
  {
    metric: "load",
    units: "number of flow items",
    currentLoad: [
      { flowCategory: "feature", value: 2 },
      { flowCategory: "defect", value: 1 },
      { flowCategory: "debt", value: 4 },
      { flowCategory: "risk", value: 3 },
    ],
  },
];

function generateArc() {
  const w = 500;
  const h = 500;

  const svg = d3
    .select("#arc")
    .append("svg")
    .attr("width", w)
    .attr("height", h);

  const sortedGDP = gdp.sort((a, b) => (a.value > b.value ? 1 : -1));
  const color = d3.scaleOrdinal(d3.schemeDark2);

  const max_gdp = d3.max(sortedGDP, (o) => o.value);

  const angleScale = d3
    .scaleLinear()
    .domain([0, max_gdp])
    .range([0, 1.5 * Math.PI]);

  const arc = d3
    .arc()
    .innerRadius((d, i) => (i + 1) * 25)
    .outerRadius((d, i) => (i + 2) * 25)
    .startAngle(angleScale(0))
    .endAngle((d) => angleScale(d.value));

  const g = svg.append("g");

  g.selectAll("path")
    .data(sortedGDP)
    .enter()
    .append("path")
    .attr("d", arc)
    .attr("fill", (d, i) => color(i))
    .attr("stroke", "#FFF")
    .attr("stroke-width", "1px")
    .on("mouseenter", function () {
      d3.select(this).transition().duration(200).attr("opacity", 0.5);
    })
    .on("mouseout", function () {
      d3.select(this).transition().duration(200).attr("opacity", 1);
    });

  g.selectAll("text")
    .data(gdp)
    .enter()
    .append("text")
    .text((d) => `${d.country} -  ${d.value} Trillion`)
    .attr("x", -150)
    .attr("dy", -8)
    .attr("y", (d, i) => -(i + 1) * 25);

  g.attr("transform", "translate(200,300)");
}

onMounted(() => {
  // generateArc();

  const chart = BarChart(load[0].currentLoad, {
    x: (d) => d.value,
    y: (d) => d.flowCategory,
    marginLeft: 60,
    marginRight: 60,
    yDomain: d3.groupSort(
      load[0].currentLoad,
      ([d]) => -d.value,
      (d) => d.flowCategory
    ), // sort by descending frequency
    xLabel: `${load[0].units} →`,
    color: "steelblue",
  });

  const svg = d3.select("#hBar").node().append(chart);
});
</script>
