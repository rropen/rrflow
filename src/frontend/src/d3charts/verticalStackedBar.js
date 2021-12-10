// Copyright 2021 Observable, Inc.
// Released under the ISC license.
// https://observablehq.com/@d3/stacked-normalized-horizontal-bar

import * as d3 from "d3";

export function verticalStackedBarChart(
  data,
  {
    x = (d, i) => i, // given d in data, returns the (quantitative) x-value
    y = (d) => d, // given d in data, returns the (ordinal) y-value
    z = () => true, // given d in data, returns the (categorical) z-value
    title, // given d in data, returns the title text
    marginTop = 30, // top margin, in pixels
    marginRight = 20, // right margin, in pixels
    marginBottom = 20, // bottom margin, in pixels
    marginLeft = 40, // left margin, in pixels
    width = 640, // outer width, in pixels
    height, // outer height, in pixels
    xDomain, // [xmin, xmax]
    xRange = [marginLeft, width - marginRight], // [left, right]
    xPadding = 0.1,
    yType = d3.scaleLinear,
    yDomain, // array of y-values
    yRange, // [bottom, top]
    zDomain, // array of z-values
    offset = d3.stackOffsetDiverging, // stack offset method
    order = d3.stackOrderNone, // stack order method
    yFormat = "%", // a format specifier string for the x-axis
    yLabel, // a label for the x-axis
    colors = d3.schemeTableau10, // array of colors
  } = {}
) {
  // Compute values.
  const X = d3.map(data, x);
  const Y = d3.map(data, y);
  const Z = d3.map(data, z);

  // Compute default y- and z-domains, and unique them.
  if (xDomain === undefined) xDomain = X;
  if (zDomain === undefined) zDomain = Z;
  xDomain = new d3.InternSet(xDomain);
  zDomain = new d3.InternSet(zDomain);

  // Omit any data not present in the y- and z-domains.
  const I = d3
    .range(X.length)
    .filter((i) => xDomain.has(X[i]) && zDomain.has(Z[i]));

  // If the height is not specified, derive it from the y-domain.
  if (height === undefined)
    height = zDomain.size * 40 + marginTop + marginBottom;
  if (yRange === undefined) yRange = [height - marginBottom, marginTop];

  // Compute a nested array of series where each series is [[x1, x2], [x1, x2],
  // [x1, x2], …] representing the x-extent of each stacked rect. In addition,
  // each tuple has an i (index) property so that we can refer back to the
  // original data point (data[i]). This code assumes that there is only one
  // data point for a given unique y- and z-value.
  const series = d3
    .stack()
    .keys(zDomain)
    .value(([x, I], z) => Y[I.get(z)])
    .order(order)
    .offset(offset)(
      d3.rollup(
        I,
        ([i]) => i,
        (i) => X[i],
        (i) => Z[i]
      )
    )
    .map((s) => s.map((d) => Object.assign(d, { i: d.data[1].get(s.key) })));

  // Compute the default y-domain. Note: diverging stacks can be negative.
  if (yDomain === undefined) yDomain = d3.extent(series.flat(2));

  // Construct scales, axes, and formats.
  const xScale = d3.scaleBand(xDomain, xRange).paddingInner(xPadding);
  const yScale = yType(yDomain, yRange);
  const color = d3.scaleOrdinal(zDomain, colors);
  const xAxis = d3.axisBottom(xScale).tickSizeOuter(0);
  const yAxis = d3.axisLeft(yScale).ticks(height / 80, yFormat);

  // Compute titles.
  if (title === undefined) {
    title = (i) => `${X[i]}\n${Z[i]}\n${Y[i].toLocaleString()}`;
  } else {
    const O = d3.map(data, (d) => d);
    const T = title;
    title = (i) => T(O[i], i, data);
  }

  const svg = d3
    .create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

  svg
    .append("g")
    .attr("transform", `translate(${marginLeft},0)`)
    .call(yAxis)
    .call((g) => g.select(".domain").remove())
    .call((g) =>
      g
        .selectAll(".tick line")
        .clone()
        .attr("x2", width - marginLeft - marginRight)
        .attr("stroke-opacity", 0.1)
    )
    .call((g) =>
      g
        .append("text")
        .attr("x", -marginLeft)
        .attr("y", 10)
        .attr("fill", "currentColor")
        .attr("text-anchor", "start")
        .text(yLabel)
    );

  const bar = svg
    .append("g")
    .selectAll("g")
    .data(series)
    .join("g")
    .attr("fill", ([{ i }]) => color(Z[i]))
    .selectAll("rect")
    .data((d) => d)
    .join("rect")
    .attr("x", ({ i }) => xScale(X[i]))
    .attr("y", ([y1, y2]) => Math.min(yScale(y1), yScale(y2)))
    .attr("height", ([y1, y2]) => Math.abs(yScale(y1) - yScale(y2)))
    .attr("width", xScale.bandwidth());

  if (title) bar.append("title").text(({ i }) => title(i));

  svg
    .append("g")
    .attr("transform", `translate(0, ${yScale(0)})`)
    .call(xAxis);

  // return Object.assign(svg.node(), {scales: {color}});
  return svg.node();
}
