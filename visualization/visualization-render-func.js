// This file contains rendering functions for data of different strategies of the simulation as well as some helper functions.
// These are used to render the data in visualization.js

// helper function to generate GeoJSON points
function createGeoJsonPoint(coords) {
  return {
    type: "Point",
    coordinates: coords, // coords has to be of the form [lon, lat]
  };
}

// helper function to generate GeoJSON polygon
function createGeoJsonPolygon(coords) {
  return {
    type: "Polygon",
    coordinates: coords,
  };
}

// renders the data using information of the BrokerBG strategy
function renderDataBrokerBG(data, colors, path) {
  let color_no = -1; // first point is a broker, sets this number to position 0
  const broker_group = d3.select("#broker");
  const data_group = d3.select("#data");
  let color_map = new Map();
  let last_color = "";
  for (let i = 0; i < data.length; i++) {
    if (data[i].function === "BrokerField") {
      // cover area of broker
      // rounding and adding/substracting of 0.05 counteracts overlap
      const rect = createGeoJsonPolygon([
        [
          [Math.round(data[i].p1x), Math.round(data[i].p1y)],
          [Math.round(data[i].p2x), Math.round(data[i].p2y)],
          [Math.round(data[i].p3x), Math.round(data[i].p3y)],
          [Math.round(data[i].p4x), Math.round(data[i].p4y)],
          [Math.round(data[i].p5x), Math.round(data[i].p5y)],
          [Math.round(data[i].p6x), Math.round(data[i].p6y)],
          [Math.round(data[i].p1x), Math.round(data[i].p1y)],
        ],
      ]);

      // select color
      color_no = (color_no + 1) % colors.length; // colors repeat
      const color = colors[color_no];
      const id = "rect_" + i;

      // generate point if it does not exist
      let rect_svg = d3.select("#" + id);
      if (rect_svg.empty()) {
        rect_svg = data_group.append("path").attr("id", id);
      }

      // render rectangle
      rect_svg
        .attr("fill", color + "77") // add transparency
        .datum(rect)
        .attr("d", path);
    } else if (data[i].function === "Broker") {
      // new broker
      const point = createGeoJsonPoint([data[i].lon, data[i].lat]); // lon, lat; has to be inverted because of GeoJson

      // select new color, if new group
      if (!color_map.has(data[i].leader)) {
        color_no = (color_no + 1) % colors.length; // colors repeat
        color_map.set(data[i].leader, colors[color_no]);
      }
      const color = color_map.get(data[i].leader);
      last_color = color; // to color rectangles in the same color
      const id = "point_" + i + "_broker";

      // generate point if it does not exist
      let point_svg = d3.select("#" + id);
      if (point_svg.empty()) {
        point_svg = broker_group.append("path").attr("id", id);
      }

      // render point
      path.pointRadius(3.5);
      point_svg.attr("fill", color).datum(point).attr("d", path);

      if (data[i].brokerId === data[i].leader) {
        // is leader
        // generate or select outline
        let point_svg_outline = d3.select("#" + id + "_outline");
        if (point_svg_outline.empty()) {
          point_svg_outline = broker_group
            .append("path")
            .attr("id", id + "_outline");
        }

        // render outline
        path.pointRadius(7);
        point_svg_outline
          .attr("fill", "none")
          .attr("stroke", color)
          .attr("stroke-width", "2.5")
          .datum(point)
          .attr("d", path);
      }
    }
  }
}

// creates a legend for the BrokerBG visualization
function createLegendBrokerBG() {
  const path = d3.geoPath();
  const legend_table = d3.select("#legend-table");

  // -- leader --
  const leader_row = legend_table.append("tr");
  const leader_svg = leader_row.append("td").append("svg");
  leader_svg.attr("height", 20).attr("width", 20);
  const leader_point = createGeoJsonPoint([10, 10]);

  // point
  path.pointRadius(3.5);
  leader_svg
    .append("path")
    .attr("fill", "black")
    .datum(leader_point)
    .attr("d", path);

  // outline
  path.pointRadius(7);
  leader_svg
    .append("path")
    .attr("fill", "none")
    .attr("stroke", "black")
    .attr("stroke-width", "2.5")
    .datum(leader_point)
    .attr("d", path);

  // text
  leader_row.append("td").text("– Leader");

  // -- member --
  const member_row = legend_table.append("tr");
  const member_svg = member_row.append("td").append("svg");
  member_svg.attr("height", 20).attr("width", 20);
  const member_point = createGeoJsonPoint([10, 10]);

  // point
  path.pointRadius(3.5);
  member_svg
    .append("path")
    .attr("fill", "black")
    .datum(member_point)
    .attr("d", path);

  // text
  member_row.append("td").text("– Member");

  // -- area --
  const broker_row2 = legend_table.append("tr");
  broker_row2.append("td").text("Colored area");
  broker_row2
    .append("td")
    .text("– Area that covers all brokers of a broadcast group");
}

// renders the data using information of the BrokerDisGBEvents or BrokerDisGBSubscriptions strategy
function renderDataBrokerDisGB(data, colors, path) {
  let color_no = -1; // first point is a broker, sets this number to position 0

  const broker_group = d3.select("#broker");
  const data_group = d3.select("#data");

  for (let i = 0; i < data.length; i++) {
    if (data[i].function === "BrokerField") {
      // cover area of broker
      // rounding and adding/substracting of 0.05 counteracts overlap
      const rect = createGeoJsonPolygon([
        [
          [
            Math.round(data[i].boxMinX) + 0.05,
            Math.round(data[i].boxMinY) + 0.05,
          ],
          [
            Math.round(data[i].boxMinX) + 0.05,
            Math.round(data[i].boxMaxY) - 0.05,
          ],
          [
            Math.round(data[i].boxMaxX) - 0.05,
            Math.round(data[i].boxMaxY) - 0.05,
          ],
          [
            Math.round(data[i].boxMaxX) - 0.05,
            Math.round(data[i].boxMinY) + 0.05,
          ],
          [
            Math.round(data[i].boxMinX) + 0.05,
            Math.round(data[i].boxMinY) + 0.05,
          ],
        ],
      ]);

      // select color matching last broker
      const color = colors[color_no];
      const id = "rect_" + i;

      // generate point if it does not exist
      let rect_svg = d3.select("#" + id);
      if (rect_svg.empty()) {
        rect_svg = data_group.append("path").attr("id", id);
      }

      // render rectangle
      rect_svg
        .attr("fill", color + "77") // add transparency
        .datum(rect)
        .attr("d", path);
    } else if (data[i].function === "Broker") {
      // new broker
      const point = createGeoJsonPoint([data[i].lon, data[i].lat]); // lon, lat; has to be inverted because of GeoJson

      // select new color
      color_no = (color_no + 1) % colors.length; // colors repeat
      const color = colors[color_no];
      const id = "point_" + i + "_broker";

      // generate point if it does not exist
      let point_svg = d3.select("#" + id);
      if (point_svg.empty()) {
        point_svg = broker_group.append("path").attr("id", id);
      }
      let point_svg_outline = d3.select("#" + id + "_outline");
      if (point_svg_outline.empty()) {
        point_svg_outline = broker_group
          .append("path")
          .attr("id", id + "_outline");
      }

      // render point
      path.pointRadius(3.5);
      point_svg.attr("fill", color).datum(point).attr("d", path);

      // render outline
      path.pointRadius(7);
      point_svg_outline
        .attr("fill", "none")
        .attr("stroke", color)
        .attr("stroke-width", "2.5")
        .datum(point)
        .attr("d", path);
    }
  }
}

// creates a legend for the BrokerDisGBEvents and BrokerDisGBSubscriptions visualization
function createLegendBrokerDisGB() {
  const path = d3.geoPath();
  const legend_table = d3.select("#legend-table");

  // -- broker --
  const broker_row = legend_table.append("tr");
  const broker_svg = broker_row.append("td").append("svg");
  broker_svg.attr("height", 20).attr("width", 20);
  const broker_point = createGeoJsonPoint([10, 10]);

  // point
  path.pointRadius(3.5);
  broker_svg
    .append("path")
    .attr("fill", "black")
    .datum(broker_point)
    .attr("d", path);

  // outline
  path.pointRadius(7);
  broker_svg
    .append("path")
    .attr("fill", "none")
    .attr("stroke", "black")
    .attr("stroke-width", "2.5")
    .datum(broker_point)
    .attr("d", path);

  // text
  broker_row.append("td").text("– Broker");

  // -- area --
  const broker_row2 = legend_table.append("tr");
  broker_row2.append("td").text("Colored area");
  broker_row2.append("td").text("– Broker area");
}

// creates a legend for the BrokerFloodingEvents and BrokerFloodingSubscriptions visualization
function createLegendBrokerFlooding() {
  const path = d3.geoPath();
  const legend_table = d3.select("#legend-table");

  // -- broker --
  const broker_row = legend_table.append("tr");
  const broker_svg = broker_row.append("td").append("svg");
  broker_svg.attr("height", 20).attr("width", 20);
  const broker_point = createGeoJsonPoint([10, 10]);

  // point
  path.pointRadius(3.5);
  broker_svg
    .append("path")
    .attr("fill", "black")
    .datum(broker_point)
    .attr("d", path);

  // outline
  path.pointRadius(7);
  broker_svg
    .append("path")
    .attr("fill", "none")
    .attr("stroke", "black")
    .attr("stroke-width", "2.5")
    .datum(broker_point)
    .attr("d", path);

  // text
  broker_row.append("td").text("– Broker");

  // -- area --
  const broker_row2 = legend_table.append("tr");
  broker_row2.append("td").text("Colored area");
  broker_row2
    .append("td")
    .text("– Area in which clients for a given broker can be located");
}

// state for quorum highlighting
var renderStateGQPS = {};
const highlight_color = "#FFCC00";
const highlight_clicked_color = "#B6B6B6";

// renders the data using information of the BrokerGQPS strategy
function renderDataBrokerGQPS(data, colors, path) {
  let color_no = -1; // first point is a broker, sets this number to position 0

  const broker_group = d3.select("#broker");
  const data_group = d3.select("#data");

  let broker_connections = new Map();

  for (let i = 0; i < data.length; i++) {
    if (data[i].function === "Broker") {
      // new broker
      const point = createGeoJsonPoint([data[i].lon, data[i].lat]); // lon, lat; has to be inverted because of GeoJson
      const id = data[i].brokerId.replace(/\s/g, ""); // remove whitespace

      // select new color
      color_no = (color_no + 1) % colors.length; // colors repeat
      let color = colors[color_no];
      if (
        renderStateGQPS.highlight !== null &&
        renderStateGQPS.highlight !== undefined
      ) {
        if (renderStateGQPS.highlight.includes(id)) {
          color = highlight_color;
        }
        if (
          renderStateGQPS.highlight[renderStateGQPS.highlight.length - 1] === id
        ) {
          color = highlight_clicked_color;
        }
      }

      const quorum = data[i].brokersInQuorum.replace(/\s/g, "").split(","); // remove whitespace and split
      broker_connections.set(id, quorum);

      // generate point if it does not exist
      let point_svg = d3.select("#" + id);
      if (point_svg.empty()) {
        point_svg = broker_group.append("path").attr("id", id);
      }
      let point_svg_outline = d3.select("#" + id + "_outline");
      if (point_svg_outline.empty()) {
        point_svg_outline = broker_group
          .append("path")
          .attr("id", id + "_outline");
      }
      let point_svg_click = d3.select("#" + id + "_click");
      if (point_svg_click.empty()) {
        point_svg_click = broker_group.append("path").attr("id", id + "_click");
      }

      // render point
      path.pointRadius(3.5);
      point_svg.attr("fill", color).datum(point).attr("d", path);
      // render outline
      path.pointRadius(7);
      point_svg_outline
        .attr("fill", "none")
        .attr("stroke", color)
        .attr("stroke-width", "2.5")
        .datum(point)
        .attr("d", path);
      // dummy element for clicking; not shown
      // I so hate the fact this seems to be necessary... can't even make it a box easily...
      // Change this as soon as pointer-events="bounding-box" of the SVG 2.0 standard becomes supported (currently only chrome)
      path.pointRadius(9);
      point_svg_click
        .attr("fill", "none")
        .attr("style", "pointer-events: all;")
        .datum(point)
        .attr("d", path)
        .on("click", function () {
          const id = this.id.substring(0, this.id.length - 6); // chop off the "_click" of id
          if (
            renderStateGQPS.highlight !== null &&
            renderStateGQPS.highlight !== undefined
          ) {
            if (
              renderStateGQPS.highlight[
                renderStateGQPS.highlight.length - 1
              ] === id
            ) {
              renderStateGQPS.highlight = null;
              renderDataBrokerGQPS(data, colors, path);
              return;
            }
          }

          const quorum = broker_connections.get(id);
          quorum.push(id);
          renderStateGQPS.highlight = quorum; // last was always clicked on
          renderDataBrokerGQPS(data, colors, path);
        });
    }
  }
}

// creates a legend for the BrokerGQPS visualization
function createLegendBrokerGQPS() {
  const broker_point = createGeoJsonPoint([10, 10]);

  const path = d3.geoPath();
  const legend_table = d3.select("#legend-table");

  // -- broker --
  const broker_row = legend_table.append("tr");
  const broker_svg = broker_row.append("td").append("svg");
  broker_svg.attr("height", 20).attr("width", 20);

  // point
  path.pointRadius(3.5);
  broker_svg
    .append("path")
    .attr("fill", "black")
    .datum(broker_point)
    .attr("d", path);

  // outline
  path.pointRadius(7);
  broker_svg
    .append("path")
    .attr("fill", "none")
    .attr("stroke", "black")
    .attr("stroke-width", "2.5")
    .datum(broker_point)
    .attr("d", path);

  // text
  broker_row.append("td").text("– Broker (can be clicked to show quorum)");

  // -- broker clicked --
  const broker_clicked_row = legend_table.append("tr");
  const broker_clicked_svg = broker_clicked_row.append("td").append("svg");
  broker_clicked_svg.attr("height", 20).attr("width", 20);

  // point
  path.pointRadius(3.5);
  broker_clicked_svg
    .append("path")
    .attr("fill", highlight_clicked_color)
    .datum(broker_point)
    .attr("d", path);

  // outline
  path.pointRadius(7);
  broker_clicked_svg
    .append("path")
    .attr("fill", "none")
    .attr("stroke", highlight_clicked_color)
    .attr("stroke-width", "2.5")
    .datum(broker_point)
    .attr("d", path);

  // text
  broker_clicked_row.append("td").text("– Broker (clicked)");

  // -- broker in quorum --
  const broker_highlight_row = legend_table.append("tr");
  const broker_highlight_svg = broker_highlight_row.append("td").append("svg");
  broker_highlight_svg.attr("height", 20).attr("width", 20);

  // point
  path.pointRadius(3.5);
  broker_highlight_svg
    .append("path")
    .attr("fill", highlight_color)
    .datum(broker_point)
    .attr("d", path);

  // outline
  path.pointRadius(7);
  broker_highlight_svg
    .append("path")
    .attr("fill", "none")
    .attr("stroke", highlight_color)
    .attr("stroke-width", "2.5")
    .datum(broker_point)
    .attr("d", path);

  // text
  broker_highlight_row.append("td").text("– Broker (part of quorum)");
}

// state for highlighting in table
var renderStateDHT = {};

// renders the data using information of the BrokerDHT strategy
function renderDataBrokerDHT(data, colors, path) {
  // process data
  if (
    renderStateDHT.brokerToTopicCount === null ||
    renderStateDHT.brokerToTopicCount === undefined ||
    renderStateDHT.maxTopics === null ||
    renderStateDHT.maxTopics === undefined
  ) {
    const broker_dht_container = d3.select("#broker-dht-container");
    const topic_table = d3.select("#topic-table");
    const topic_table_header = topic_table.append("tr");
    topic_table_header.append("td").html("BrokerID");
    topic_table_header.append("td").html("No of distinct Topics");

    let brokerToTopicCount = new Array(0);
    let maxTopics = 0;

    for (let i = 0; i < data.length; i++) {
      if (data[i].topics !== "null") {
        const currBrokerTopics = data[i].topics.replace(/\s/g, "").split(","); // remove whitespace and split

        brokerToTopicCount[i] = currBrokerTopics.length;
        if (maxTopics < brokerToTopicCount[i]) {
          maxTopics = brokerToTopicCount[i];
        }
      } else {
        brokerToTopicCount[i] = 0;
      }

      // build table
      const id = data[i].brokerId.replace(/\s/g, ""); // remove whitespace

      const broker_topic_row = topic_table.append("tr");
      broker_topic_row.attr("id", id + "_table");
      broker_topic_row.append("td").html(data[i].brokerId);
      broker_topic_row.append("td").html(brokerToTopicCount[i]);
    }

    renderStateDHT.brokerToTopicCount = brokerToTopicCount;
    renderStateDHT.maxTopics = maxTopics;

    // make table visible
    broker_dht_container.style("display", "initial");
  }
  let colormapDHT = [
    "#a2c9e6",
    "#7ab4e1",
    "#509edf",
    "#2387e0",
    "#146ec2",
    "#0b559f",
  ];

  const broker_group = d3.select("#broker");
  const data_group = d3.select("#data");

  for (let i = 0; i < data.length; i++) {
    if (data[i].function === "Broker") {
      // new broker
      const point = createGeoJsonPoint([data[i].lon, data[i].lat]); // lon, lat; has to be inverted because of GeoJson
      const id = data[i].brokerId.replace(/\s/g, ""); // remove whitespace

      // select color based on number of topics
      // this calculation returns a value in the interval [0,colormapDHT.length], where the maximum value
      // only occurs at the exact edge (i.e. only for maxTopics)
      // this is fixed by setting everything above colormap.length - 1 to that value afterwards
      let color_no = Math.floor(
        (renderStateDHT.brokerToTopicCount[i] / renderStateDHT.maxTopics) *
          colormapDHT.length
      );
      if (color_no >= colormapDHT.length) {
        color_no = colormapDHT.length - 1; // clip to last available color
      }
      let color = colormapDHT[color_no];

      if (
        renderStateDHT.highlight !== null &&
        renderStateDHT.highlight !== undefined
      ) {
        if (renderStateDHT.highlight === id) {
          color = highlight_color;
          d3.select("#" + id + "_table").style(
            "background-color",
            highlight_color
          );
        }
      }

      // generate point if it does not exist
      let point_svg = d3.select("#" + id);
      if (point_svg.empty()) {
        point_svg = broker_group.append("path").attr("id", id);
      }
      let point_svg_outline = d3.select("#" + id + "_outline");
      if (point_svg_outline.empty()) {
        point_svg_outline = broker_group
          .append("path")
          .attr("id", id + "_outline");
      }
      let point_svg_click = d3.select("#" + id + "_click");
      if (point_svg_click.empty()) {
        point_svg_click = broker_group.append("path").attr("id", id + "_click");
      }

      // render point
      path.pointRadius(3.5);
      point_svg.attr("fill", color).datum(point).attr("d", path);
      // render outline
      path.pointRadius(7);
      point_svg_outline
        .attr("fill", "none")
        .attr("stroke", color)
        .attr("stroke-width", "2.5")
        .datum(point)
        .attr("d", path);
      // dummy element for clicking; not shown
      // I so hate the fact this seems to be necessary... can't even make it a box easily...
      // Change this as soon as pointer-events="bounding-box" of the SVG 2.0 standard becomes supported (currently only chrome)
      path.pointRadius(9);
      point_svg_click
        .attr("fill", "none")
        .attr("style", "pointer-events: all;")
        .datum(point)
        .attr("d", path)
        .on("click", function () {
          const id = this.id.substring(0, this.id.length - 6); // chop off the "_click" of id
          if (
            renderStateDHT.highlight !== null &&
            renderStateDHT.highlight !== undefined
          ) {
            d3.select("#" + renderStateDHT.highlight + "_table").style(
              "background-color",
              "initial"
            );
            if (renderStateDHT.highlight === id) {
              renderStateDHT.highlight = null;
              renderDataBrokerDHT(data, colors, path);
              return;
            }
          }

          renderStateDHT.highlight = id; // last was always clicked on
          renderDataBrokerDHT(data, colors, path);
        });
    }
  }
}

// creates a legend for the BrokerDHT visualization
function createLegendBrokerDHT() {
  const broker_point = createGeoJsonPoint([10, 10]);

  const path = d3.geoPath();
  const legend_table = d3.select("#legend-table");

  // -- broker --
  const broker_row = legend_table.append("tr");
  const broker_svg = broker_row.append("td").append("svg");
  broker_svg.attr("height", 20).attr("width", 20);

  // point
  path.pointRadius(3.5);
  broker_svg
    .append("path")
    .attr("fill", "black")
    .datum(broker_point)
    .attr("d", path);

  // outline
  path.pointRadius(7);
  broker_svg
    .append("path")
    .attr("fill", "none")
    .attr("stroke", "black")
    .attr("stroke-width", "2.5")
    .datum(broker_point)
    .attr("d", path);

  // text
  broker_row
    .append("td")
    .text("– Broker (can be clicked to highlight corresponding row in table)");

  // -- text for colormap --
  let colormapDHT = [
    "#a2c9e6",
    "#7ab4e1",
    "#509edf",
    "#2387e0",
    "#146ec2",
    "#0b559f",
  ];

  const colormap_row = legend_table.append("tr");
  const colormap_svg = colormap_row
    .append("td")
    .append("svg")
    .attr("height", 20)
    .attr("width", 120);

  for (let i = 0; i < colormapDHT.length; i++) {
    colormap_svg
      .append("rect")
      .attr("width", 20)
      .attr("height", 20)
      .attr("x", 0 + i * 20)
      .attr("y", 0)
      .attr("fill", colormapDHT[i]);
  }

  colormap_row
    .append("td")
    .html("– Broker colors, from 0 topics to most individual topics");
}

function createLegend(type) {
  const legend_table = d3.select("#legend-table");
  legend_table.html(null);
  switch (type) {
    case "broker-bg":
      createLegendBrokerBG();
      break;
    case "broker-dis-gb-events":
      createLegendBrokerDisGB();
      break;
    case "broker-dis-gb-subscriptions":
      createLegendBrokerDisGB();
      break;
    case "broker-flooding-events":
      createLegendBrokerFlooding();
      break;
    case "broker-flooding-subscriptions":
      createLegendBrokerFlooding();
      break;
    case "broker-gqps":
      createLegendBrokerGQPS();
      break;
    case "broker-dht":
      createLegendBrokerDHT();
      break;
    default:
      // no-data
      createLegendBrokerDisGB();
      break;
  }
}

function clearState() {
  const broker_dht_container = d3.select("#broker-dht-container");
  const topic_table = d3.select("#topic-table");
  renderStateGQPS = {};
  renderStateDHT = {};
  broker_dht_container.style("display", "none");
  topic_table.html(null);
}
