// Code taken and changed from: https://github.com/MoeweX/DisGB-Simulation

var lastTime = d3.now()
var autorotate, path, land110, land50, ground_stations;
var current_layer = null

// function for data rendering to svg
// the path returned by createPathAndPrepSvg is required for correct rendering
// arguments:
// - land (to render continents)
// - keygroups (to render keygroups)
// - path (to generate svg paths with correct projection)
// - ground_stations (ground stations to generate)
function render(land, keygroups, path, ground_stations) {
    // standard colors from seaborn
    const colors = [
      "#4c72b0",
      "#dd8452",
      "#55a868",
      "#c44e52",
      "#8172b3",
      "#937860",
      "#da8bc3",
      "#8c8c8c",
      "#ccb974",
      "#64b5cd",
      "#2e456b",
      "#865032",
      "#34663f",
      "#772f32",
      "#4e456d",
      "#59493a",
      "#845476",
      "#666666",
      "#7c7046",
      "#3d6e7c",
      "#9b59b6",
      "#3498db",
      "#95a5a6",
      "#e74c3c",
      "#34495e",
      "#2ecc71",
    ];
  
    // get svg
    const map_svg = d3.select("#visualization-svg");
  
    // rendering of sphere with countries
    map_svg.select("#land").datum(land).attr("d", path);
    if (data !== null) {
        renderKeygroups(keygroups, colors, path);
        renderGroundStations(ground_stations, path)
    }
}
// Note: brokertypefromfilename: do not have and need that

function boundNumberToInterval(number, min, max) {
    if (max < min) {
      // sanity check; do nothing
      return number;
    }
    if (number < min) {
      // bound at min
      return min;
    }
    if (number > max) {
      // bound at max
      return max;
    }
    return number;
}

function startRotation(delay, projection) {
  console.log("start Rotation")
  autorotate.restart((elapsed) => {
    now = d3.now()
    diff = now - lastTime
    if (diff < elapsed) {
      rotation = projection.rotate()
      rotation[0] += diff * (6/1000)
      projection.rotate(rotation)
      render(land110, current_layer, path, ground_stations) //or land 50?
    }
    lastTime = now
  }, delay || 0)
}

function stopRotation() {
  console.log("stop rotation")
  autorotate.stop()
}

// function for dragging the projection, translating mouse drag with versor into rotations
// of the projection
function drag(projection) {
    let v0, q0, r0;
  
    function dragstarted() {
      // state at beginning of click
      const coords = [d3.event.x - 10, d3.event.y - 10]; // -10px to correct for svg viewbox
      v0 = versor.cartesian(projection.invert(coords));
      q0 = versor((r0 = projection.rotate()));
      stopRotation()
    }
  
    function dragged() {
      // update while dragging
      const coords = [d3.event.x - 10, d3.event.y - 10]; // -10px to correct for svg viewbox
      const v1 = versor.cartesian(projection.rotate(r0).invert(coords));
      const q1 = versor.multiply(q0, versor.delta(v0, v1));
      projection.rotate(versor.rotation(q1));
    }

    function dragended() {
      startRotation(3000, projection)
    }
  
    return d3.drag().on("start", dragstarted).on("drag", dragged).on('end', dragended);
}

function getResponseText(response) {
    if (!response.ok) {
      return null;
    }
    return response.text();
  }
  
  function parseResponse(response) {
    const format = d3.dsvFormat(";");
    if (response === null) {
      return null;
    }
    return format.parse(response);
  }

function clearDataFromSvg() {
// get svg
const map_svg = d3.select("#visualization-svg");

map_svg.select("#data").html(null);
map_svg.select("#broker").html(null);
clearState();
}

(async function () {
    const file_menu = d3.select("#layer-selection");

    let local_data = null;
    function localDataListener(event) {
      let reader = new FileReader();
  
      let file = event.target.files[0];
  
      reader.addEventListener("load", parseFile, false);
      if (file) {
        reader.readAsText(file);
      }
  
      function parseFile() {
        const format = d3.dsvFormat(";");
        local_data = format.parse(reader.result);
        // local_data_type = getBrokerTypeFromFilename(filename);
  
        let dropdown = document.getElementById("layer-selection");
        dropdown.dispatchEvent(new Event("change")); // fire event to indicate the change
      }
    }

    // -- loading of all the data, synchronous with await --
    // load and parse available files
    const first_layer = await fetch("CSV/keygroups_1.csv")
      .then(getResponseText)
      .then(parseResponse);
    if (first_layer != null) {
      file_menu.select("#first-layer").property("disabled", false);
      current_layer = first_layer
    }

    const second_layer = await fetch("CSV/keygroups_2.csv")
      .then(getResponseText)
      .then(parseResponse);
    if (second_layer != null) {
      file_menu.select("#second-layer").property("disabled", false);
    }

    // TODO load ground station data here
    ground_stations = await fetch("CSV/ground_stations.csv")
      .then(getResponseText)
      .then(parseResponse);
  
    // load data of continents from world-atlas
    land110 = await d3
      .json("https://cdn.jsdelivr.net/npm/world-atlas@2/land-110m.json")
      .then((json) => topojson.feature(json, json.objects.land));
    land50 = await d3
      .json("https://cdn.jsdelivr.net/npm/world-atlas@2/land-50m.json")
      .then((json) => topojson.feature(json, json.objects.land));
   
    // object for projection
    const sphere = { type: "Sphere" };
  
    // get svg
    const map_svg = d3.select("#visualization-svg");
  
    // generate elements for svg
    map_svg.append("path").attr("id", "sphere_fill");
    map_svg.append("path").attr("id", "sphere_outline");
    map_svg.append("path").attr("id", "land");
    map_svg.append("g").attr("id", "data");
    map_svg.append("g").attr("id", "broker");
  
    // function to calculate settings for projection and svg and create path object for rendering
    // it has a lot of side effects and can not be called whenever!
    // returns d3.geoPath, needed for rendering
    function createPathAndPrepSvg(projection, width) {
      // calculate height from width for canvas and scale projection appropriately
      const [[x0, y0], [x1, y1]] = d3
        .geoPath(projection.fitWidth(width, sphere))
        .bounds(sphere);
      const dy = Math.ceil(y1 - y0),
        l = Math.min(Math.ceil(x1 - x0), dy);
      projection.scale((projection.scale() * (l - 1)) / l).precision(0.2);
      const height = dy;
  
      // create d3 path generator
      const path = d3.geoPath().projection(projection);
  
      // set width and height
      map_svg
        .attr("width", width + 20)
        .attr("height", height + 20)
        .attr("viewBox", "-10 -10 " + (width + 20) + " " + (height + 20)); // leave 10px on each side
  
      // create some rendered elements
      map_svg
        .select("#sphere_fill")
        .attr("fill", "#e6e6e6")
        .datum(sphere)
        .attr("d", path);
      map_svg
        .select("#sphere_outline")
        .attr("fill", "none")
        .attr("stroke", "#4d4d4d")
        .datum(sphere)
        .attr("d", path);
  
      // render svg and make it draggable
      map_svg
        .call(
          drag(projection)
            .on("drag.render", () => render(land110, current_layer, path, ground_stations))
            .on("end.render", () => render(land50, current_layer,path, ground_stations)))
        .call(() => render(land50, first_layer, path, ground_stations));
  
      return path;
    }
  
    // initial projection used on canvas, is used by the projectionListener
    // to keep rotation between projection changes
    let projection = d3.geoOrthographic().precision(0.1);
  
    // initial width of svg
    let width = 640;
  
    // create path and prepare svg
    path = createPathAndPrepSvg(projection, width);

    // autorotation
    autorotate = d3.timer((elapsed) => {
      now = d3.now()
      diff = now - lastTime
      if (diff < elapsed) {
        rotation = projection.rotate()
        rotation[0] += diff * (6/1000)
        projection.rotate(rotation)
        render(land110, current_layer, path, ground_stations) //or land 50?
      }
      lastTime = now
    }, 150);

    function dataListener() {
        layer_value = this.value;
        const legend_container = d3.select("#legend-container");
        switch (layer_value) {
            case "0":
                legend_container.style("display", "initial");
                current_layer = first_layer;
                // TODO createLegend();
                break;
            case "1": 
                legend_container.style("display", "initial");
                current_layer = second_layer
                break;
            default:
                // no-data
                legend_container.style("display", "none");
                current_layer = null;
                break;
        }
        clearDataFromSvg();
        render(land50, current_layer, path, ground_stations);
      }
    // create listeners for input of rotation angles
    function sliderListener() {
        const correctedValue = boundNumberToInterval(this.value, 0, 8000); 
        document.getElementById("timestep").value = correctedValue;
        document.getElementById("timestep-val").value = correctedValue;
    }

    document.getElementById("layer-selection").onchange = dataListener;
    document.getElementById("timestep").oninput = sliderListener;
    document.getElementById("timestep-val").oninput = sliderListener;
})();

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

function renderKeygroups(data, colors, path){
    const data_group = d3.select("#data");
    for (let i = 0; i < data.length; i++) {
        let rect = null
        if (data[i].type === "hex") {
            // cover area of broker
            // rounding and adding/substracting of 0.05 counteracts overlap
            rect = createGeoJsonPolygon([
                [
                [Math.round(data[i].lon7), Math.round(data[i].lat7)],
                [Math.round(data[i].lon6), Math.round(data[i].lat6)],
                [Math.round(data[i].lon5), Math.round(data[i].lat5)],
                [Math.round(data[i].lon4), Math.round(data[i].lat4)],
                [Math.round(data[i].lon3), Math.round(data[i].lat3)],
                [Math.round(data[i].lon2), Math.round(data[i].lat2)],
                [Math.round(data[i].lon1), Math.round(data[i].lat1)],
                ],
            ]);

        } else if (data[i].type === "pent"){
            // cover area of broker
            // rounding and adding/substracting of 0.05 counteracts overlap
            rect = createGeoJsonPolygon([
                [
                [Math.round(data[i].lon6), Math.round(data[i].lat6)],
                [Math.round(data[i].lon5), Math.round(data[i].lat5)],
                [Math.round(data[i].lon4), Math.round(data[i].lat4)],
                [Math.round(data[i].lon3), Math.round(data[i].lat3)],
                [Math.round(data[i].lon2), Math.round(data[i].lat2)],
                [Math.round(data[i].lon1), Math.round(data[i].lat1)],
                ],
            ]);
        } else if (data[i].type === "hept") { 
            rect = createGeoJsonPolygon([
                [
                [Math.round(data[i].lon1), Math.round(data[i].lat1)],
                [Math.round(data[i].lon7), Math.round(data[i].lat7)],
                [Math.round(data[i].lon6), Math.round(data[i].lat6)],
                [Math.round(data[i].lon5), Math.round(data[i].lat5)],
                [Math.round(data[i].lon4), Math.round(data[i].lat4)],
                [Math.round(data[i].lon3), Math.round(data[i].lat3)],
                [Math.round(data[i].lon2), Math.round(data[i].lat2)],
                [Math.round(data[i].lon1), Math.round(data[i].lat1)],
                ],
            ]);
        } else if (data[i].type === "oct") { 
          rect = createGeoJsonPolygon([
              [
              [Math.round(data[i].lon1), Math.round(data[i].lat1)],
              [Math.round(data[i].lon8), Math.round(data[i].lat8)],
              [Math.round(data[i].lon7), Math.round(data[i].lat7)],
              [Math.round(data[i].lon6), Math.round(data[i].lat6)],
              [Math.round(data[i].lon5), Math.round(data[i].lat5)],
              [Math.round(data[i].lon4), Math.round(data[i].lat4)],
              [Math.round(data[i].lon3), Math.round(data[i].lat3)],
              [Math.round(data[i].lon2), Math.round(data[i].lat2)],
              [Math.round(data[i].lon1), Math.round(data[i].lat1)],
              ],
          ]);
        } else if (data[i].type === "dec") { 
          rect = createGeoJsonPolygon([
              [
              [Math.round(data[i].lon1), Math.round(data[i].lat1)],
              [Math.round(data[i].lon10), Math.round(data[i].lat10)],
              [Math.round(data[i].lon9), Math.round(data[i].lat9)],
              [Math.round(data[i].lon8), Math.round(data[i].lat8)],
              [Math.round(data[i].lon7), Math.round(data[i].lat7)],
              [Math.round(data[i].lon6), Math.round(data[i].lat6)],
              [Math.round(data[i].lon5), Math.round(data[i].lat5)],
              [Math.round(data[i].lon4), Math.round(data[i].lat4)],
              [Math.round(data[i].lon3), Math.round(data[i].lat3)],
              [Math.round(data[i].lon2), Math.round(data[i].lat2)],
              [Math.round(data[i].lon1), Math.round(data[i].lat1)],
              ],
          ]);
        }
        if (rect !== null) {
            // select color
            const color = colors[i % colors.length];
            // const id = "keygroup_" + data[i].id;
            const id = "keygroup_"+data[i].id;

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
        } else {
            console.log("sth is not working")
        } 
    }
}

function renderGroundStations(data, path){
  const data_group = d3.select("#data");
  const color = "orange"
    for (let i = 0; i < data.length; i++) {
      const point = createGeoJsonPoint([data[i].lng, data[i].lat]); // lon, lat; has to be inverted because of GeoJson
      const id = "ground_station"+i;
      
      // generate point if it does not exist
      let point_svg = d3.select("#"+id);
      if (point_svg.empty()) {
          point_svg = data_group.append("path")
              .attr("id", id);
      }

      // render point
      path.pointRadius(3.5)
      point_svg
          .attr("fill", color)
          .datum(point)
          .attr("d", path);

      // generate or select outline
      let point_svg_outline = d3.select("#"+id+"_outline");
      if (point_svg_outline.empty()) {
          point_svg_outline = data_group.append("path")
              .attr("id", id+"_outline");
      }

      // render outline
      path.pointRadius(7)
      point_svg_outline
          .attr("fill", "none")
          .attr("stroke", color)
          .attr("stroke-width", "2.5")
          .datum(point)
          .attr("d", path);
    
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