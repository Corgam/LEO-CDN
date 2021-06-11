// script dependencies (have to be loaded in html before this file)
// d3js v5
// topojson-client 3
// versor 0.1.2
// FileSaver.js 2.0.2

// data dependencies (have to be available for this script to function)
// world-atlas 2 (via jsdeliver CDN)

// The website using this script has to be loaded via an http server serving on localhost:8080
// for loading of the CSV to function, though the location can be changed.
// Since local data can not be loaded due to modern security restrictions, the CSV data has
// to be loaded from an http server.

// returns number if in bounds, or closest bound if outside
function boundNumberToInterval(number, min, max) {
    if (max < min) { // sanity check; do nothing
        return number;
    }
    if (number < min) { // bound at min
        return min;
    }
    if (number > max) { // bound at max
        return max;
    }
    return number;
}

// function for dragging the projection, translating mouse drag with versor into rotations
// of the projection
function drag(projection) {
    let v0, q0, r0;

    function dragstarted() {
        // state at beginning of click
        const coords = [d3.event.x-10, d3.event.y-10] // -10px to correct for svg viewbox
        v0 = versor.cartesian(projection.invert(coords));
        q0 = versor(r0 = projection.rotate());
    }

    function dragged() {
        // update while dragging
        const coords = [d3.event.x-10, d3.event.y-10] // -10px to correct for svg viewbox
        const v1 = versor.cartesian(projection.rotate(r0).invert(coords));
        const q1 = versor.multiply(q0, versor.delta(v0, v1));
        projection.rotate(versor.rotation(q1));

        // update sliders
        const rotation = projection.rotate(); // get angles
        document.getElementById("lambda").value = rotation[0];
        document.getElementById("lambda-val").value = rotation[0];
        document.getElementById("phi").value = rotation[1];
        document.getElementById("phi-val").value = rotation[1];
        document.getElementById("gamma").value = rotation[2];
        document.getElementById("gamma-val").value = rotation[2];
    }

    return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged);
}

function clearDataFromSvg() {
    // get svg
    const map_svg = d3.select("#visualization-svg")

    map_svg.select("#data").html(null);
    map_svg.select("#broker").html(null);
    clearState();
}

// function for data rendering to svg
// the path returned by createPathAndPrepSvg is required for correct rendering
// arguments:
// - land (to render continents)
// - data (to render as points)
// - path (to generate svg paths with correct projection)
function render(land, data, type, path) {
    // standard colors from seaborn
    const colors = ["#4c72b0","#dd8452","#55a868","#c44e52","#8172b3","#937860","#da8bc3","#8c8c8c","#ccb974","#64b5cd",
                    "#2e456b","#865032","#34663f","#772f32","#4e456d","#59493a","#845476","#666666","#7c7046","#3d6e7c",
                    "#9b59b6","#3498db","#95a5a6","#e74c3c","#34495e","#2ecc71"];

    // get svg
    const map_svg = d3.select("#visualization-svg")

    // rendering of sphere with countries
    map_svg.select("#land")
        .datum(land)
        .attr("d", path);

    // rendering of data
    // the render functions are loaded from visualization-render-func.js (loaded in HTML file)
    switch (type) {
        case "broker-bg":
            renderDataBrokerBG(data, colors, path);
            break;
        case "broker-dis-gb-events":
            renderDataBrokerDisGB(data, colors, path);
            break;
        case "broker-dis-gb-subscriptions":
            renderDataBrokerDisGB(data, colors, path);
            break;
        case "broker-flooding-events":
            renderDataBrokerDisGB(data, colors, path);
            break;
        case "broker-flooding-subscriptions":
            renderDataBrokerDisGB(data, colors, path);
            break;
        case "broker-gqps":
            renderDataBrokerGQPS(data, colors, path);
            break;
        case "broker-dht":
            renderDataBrokerDHT(data, colors, path);
            break;
        default: // no-data
            break;
    }
}

// listener for the download button, attached at the very end
function downloadListener() {
    const svg = document.getElementById("visualization-container").innerHTML.trim();

    const blob = new Blob([svg], {
        type: "image/svg+xml;charset=utf-8"
    });
    saveAs(blob, "visualization.svg");
}

function getBrokerTypeFromFilename(filename) {
    let regex = /-Broker.+_brokers\.csv/;
    let match = filename.match(regex);
    if (match === null) { // wrong filename
        return null;
    }
    let result = match[0].substring(1, match[0].length-12);
    switch (result) {
        case "BrokerBG":
            return "broker-bg";
        case "BrokerDisGBEvents":
            return "broker-dis-gb-events";
        case "BrokerDisGBSubscriptions":
            return "broker-dis-gb-subscriptions";
        case "BrokerFloodingEvents":
            return "broker-flooding-events";
        case "BrokerFloodingSubscriptions":
            return "broker-flooding-subscriptions";
        case "BrokerGQPS":
            return "broker-gqps";
        case "BrokerDHT":
            return "broker-dht";
        default: // unsupported type
            return null;
    }
    return result
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

// asynchronous context, so that await is available and does not block DOM loading
// all the logic is implemented here and this function is called immediately
(async function() {
    const file_menu = d3.select("#file-dropdown");

    let local_data = null;
    let local_data_type = null;
    function localDataListener(event) {
        let reader = new FileReader();

        let file = event.target.files[0];
        let filename = file.name;

        reader.addEventListener("load", parseFile, false);
        if (file) {
            reader.readAsText(file);
        }

        function parseFile() {
            const format = d3.dsvFormat(";");
            local_data = format.parse(reader.result);
            local_data_type = getBrokerTypeFromFilename(filename);

            file_menu.select("#local-data-drop")
                .property("disabled", false);

            let dropdown = document.getElementById("file-dropdown");
            dropdown.options.selectedIndex = 5; // select Local Data
            dropdown.dispatchEvent(new Event("change")); // fire event to indicate the change
        }
    }
    document.getElementById("local-data").addEventListener("change", localDataListener);
    // -- loading of all the data, synchronous with await --
    // load and parse available files
    const broker_bg = await fetch("CSV/input-BrokerBG_brokers.csv")
        .then(getResponseText).then(parseResponse);
    const broker_dis_gb_events = await fetch("CSV/input-BrokerDisGBEvents_brokers.csv")
        .then(getResponseText).then(parseResponse);
    const broker_dis_gb_subscriptions = await fetch("CSV/input-BrokerDisGBSubscriptions_brokers.csv")
        .then(getResponseText).then(parseResponse);
    const broker_flooding_events = await fetch("CSV/input-BrokerFloodingEvents_brokers.csv")
        .then(getResponseText).then(parseResponse);
    const broker_flooding_subscriptions = await fetch("CSV/input-BrokerFloodingSubscriptions_brokers.csv")
        .then(getResponseText).then(parseResponse);
    const broker_gqps = await fetch("CSV/input-BrokerGQPS_brokers.csv")
        .then(getResponseText).then(parseResponse);
    const broker_dht = await fetch("CSV/input-BrokerDHT_brokers.csv")
        .then(getResponseText).then(parseResponse);

    if (broker_bg != null) {
        file_menu.select("#broker-bg")
            .property("disabled", false);
    }
    if (broker_dis_gb_events != null) {
        file_menu.select("#broker-dis-gb-events")
            .property("disabled", false);
    }
    if (broker_dis_gb_subscriptions != null) {
        file_menu.select("#broker-dis-gb-subscriptions")
            .property("disabled", false);
    }
    if (broker_flooding_events != null) {
        file_menu.select("#broker-flooding-events")
            .property("disabled", false);
    }
    if (broker_flooding_subscriptions != null) {
        file_menu.select("#broker-flooding-subscriptions")
            .property("disabled", false);
    }
    if (broker_gqps != null) {
        file_menu.select("#broker-gqps")
            .property("disabled", false);
    }
    if (broker_dht != null) {
        file_menu.select("#broker-dht")
            .property("disabled", false);
    }

    // load data of continents from world-atlas
    const land110 = await d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/land-110m.json")
        .then(json => topojson.feature(json, json.objects.land));
    const land50 = await d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/land-50m.json")
        .then(json => topojson.feature(json, json.objects.land));
    // standard data
    var broker_data = null;
    var broker_data_type = "no-data";

    // object for projection
    const sphere = ({type: "Sphere"})

    // get svg
    const map_svg = d3.select("#visualization-svg")

    // generate elements for svg
    map_svg.append("path")
        .attr("id", "sphere_fill");
    map_svg.append("path")
        .attr("id", "sphere_outline");
    map_svg.append("path")
        .attr("id", "land");
    map_svg.append("g")
        .attr("id", "data");
    map_svg.append("g")
        .attr("id", "broker");

    // function to calculate settings for projection and svg and create path object for rendering
    // it has a lot of side effects and can not be called whenever!
    // returns d3.geoPath, needed for rendering
    function createPathAndPrepSvg(projection, width) {
        // calculate height from width for canvas and scale projection appropriately
        const [[x0, y0], [x1, y1]] = d3.geoPath(projection.fitWidth(width, sphere)).bounds(sphere);
        const dy = Math.ceil(y1 - y0), l = Math.min(Math.ceil(x1 - x0), dy);
        projection.scale(projection.scale() * (l - 1) / l).precision(0.2);
        const height = dy;

        // create d3 path generator
        const path = d3.geoPath().projection(projection);

        // set width and height
        map_svg
            .attr("width", width+20)
            .attr("height", height+20)
            .attr("viewBox", "-10 -10 " + (width+20) + " " + (height+20)); // leave 10px on each side

        // create some rendered elements
        map_svg.select("#sphere_fill")
            .attr("fill", "#e6e6e6")
            .datum(sphere)
            .attr("d", path);
        map_svg.select("#sphere_outline")
            .attr("fill", "none")
            .attr("stroke", "#4d4d4d")
            .datum(sphere)
            .attr("d", path);

        // render svg and make it draggable
        map_svg
            .call(drag(projection)
                .on("drag.render", () => render(land110, broker_data, broker_data_type, path))
                .on("end.render", () => render(land50, broker_data, broker_data_type, path)))
            .call(() => render(land50, broker_data, broker_data_type, path))

        return path
    }

    // initial projection used on canvas, is used by the projectionListener
    // to keep rotation between projection changes
    let projection = d3.geoOrthographic().precision(0.1);

    // initial width of svg
    let width = 640;

    // create path and prepare svg
    let path = createPathAndPrepSvg(projection, width);

    // create listeners for input of rotation angles
    function lambdaListener() {
        const angle = boundNumberToInterval(this.value, -180, 180); // makes number cut off at -180 and 180
        const rotation = projection.rotate();
        projection.rotate([angle, rotation[1], rotation[2]]);
        render(land50, broker_data, broker_data_type, path);
        document.getElementById("lambda").value = angle;
        document.getElementById("lambda-val").value = angle;
    }

    function phiListener() {
        const angle = boundNumberToInterval(this.value, -180, 180); // makes number cut off at -180 and 180
        const rotation = projection.rotate();
        projection.rotate([rotation[0], angle, rotation[2]]);
        render(land50, broker_data, broker_data_type, path);
        document.getElementById("phi").value = angle;
        document.getElementById("phi-val").value = angle;
    }

    function gammaListener() {
        const angle = boundNumberToInterval(this.value, -180, 180); // makes number cut off at -180 and 180
        const rotation = projection.rotate();
        projection.rotate([rotation[0], rotation[1], angle]);
        render(land50, broker_data, broker_data_type, path);
        document.getElementById("gamma").value = angle;
        document.getElementById("gamma-val").value = angle;
    }

    function resetListener() {
        projection.rotate([0, 0, 0]);
        render(land50, broker_data, broker_data_type, path);
        document.getElementById("lambda").value = 0;
        document.getElementById("lambda-val").value = 0;
        document.getElementById("phi").value = 0;
        document.getElementById("phi-val").value = 0;
        document.getElementById("gamma").value = 0;
        document.getElementById("gamma-val").value = 0;
    }

    function dataListener() {
        broker_data_type = this.value;
        const legend_container = d3.select("#legend-container");
        switch (broker_data_type) {
            case "broker-bg":
                legend_container.style("display", "initial");
                broker_data = broker_bg;
                createLegend(broker_data_type);
                break;
            case "broker-dis-gb-events":
                legend_container.style("display", "initial");
                broker_data = broker_dis_gb_events;
                createLegend(broker_data_type);
                break;
            case "broker-dis-gb-subscriptions":
                legend_container.style("display", "initial");
                broker_data = broker_dis_gb_subscriptions;
                createLegend(broker_data_type);
                break;
            case "broker-flooding-events":
                legend_container.style("display", "initial");
                broker_data = broker_flooding_events;
                createLegend(broker_data_type);
                break;
            case "broker-flooding-subscriptions":
                legend_container.style("display", "initial");
                broker_data = broker_flooding_subscriptions;
                createLegend(broker_data_type);
                break;
            case "broker-gqps":
                legend_container.style("display", "initial");
                broker_data = broker_gqps;
                createLegend(broker_data_type);
                break;
            case "broker-dht":
                legend_container.style("display", "initial");
                broker_data = broker_dht;
                createLegend(broker_data_type);
                break;
            case "local-data":
                legend_container.style("display", "initial");
                broker_data = local_data;
                broker_data_type = local_data_type;
                createLegend(broker_data_type);
                break;
            default: // no-data
                legend_container.style("display", "none");
                broker_data = null;
                break;
        }
        clearDataFromSvg();
        render(land50, broker_data, broker_data_type, path);
    }

    // listener for dropdown menu to set projection dynamically
    function projectionListener() {
        // get rotation angles of old projection
        const rotation = projection.rotate();

        // determine selected projection
        switch (this.value) {
            case "azimuthalequalarea":
                projection = d3.geoAzimuthalEqualArea().precision(0.1);
                break;
            case "azimuthalequidistant":
                projection = d3.geoAzimuthalEquidistant().precision(0.1);
                break;
            case "gnomonic":
                projection = d3.geoGnomonic().precision(0.1);
                break;
            case "orthographic":
                projection = d3.geoOrthographic().precision(0.1);
                break;
            case "stereographic":
                projection = d3.geoStereographic().precision(0.1);
                break;
            case "equalearth":
                projection = d3.geoEqualEarth().precision(0.1);
                break;
            case "conicequalarea":
                projection = d3.geoConicEqualArea().precision(0.1);
                break;
            case "conicequidistant":
                projection = d3.geoConicEquidistant().precision(0.1);
                break;
            case "equirectangular":
                projection = d3.geoEquirectangular().precision(0.1);
                break;
            case "mercator":
                projection = d3.geoMercator().precision(0.1);
                break;
            case "transversemercator":
                projection = d3.geoTransverseMercator().precision(0.1);
                break;
            case "naturalearth1":
                projection = d3.geoNaturalEarth1().precision(0.1);
                break;
            default:
                return;
        }
        // give new projection the old rotation
        projection.rotate(rotation);
        // recreate path and recalculate svg content
        path = createPathAndPrepSvg(projection, width);
    }

    // allows width to be set dynamically
    function widthListener() {
        const new_width = boundNumberToInterval(this.value, 100, 2000); // makes number cut off at 100 and 2000
        // make sure width is an integer
        width = parseInt(new_width, 10);
        // set size of container
        document.getElementById("visualization-container").style.width = width + "px";
        document.getElementById("width-val").value = width;
        path = createPathAndPrepSvg(projection, width);
    }

    // shows/hides DHT table
    function dhtTableListener() {
        const table = d3.select("#topic-table");
        if (this.value === "Hide Table") {
            table.style("display", "none");
            this.value = "Show Table";
        } else {
            table.style("display", "initial");
            this.value = "Hide Table";
        }
    }

    // attach listeners to slider and number field
    document.getElementById("lambda").oninput = lambdaListener;
    document.getElementById("lambda-val").oninput = lambdaListener;
    document.getElementById("phi").oninput = phiListener;
    document.getElementById("phi-val").oninput = phiListener;
    document.getElementById("gamma").oninput = gammaListener;
    document.getElementById("gamma-val").oninput = gammaListener;

    document.getElementById("btn-reset").addEventListener('click', resetListener);

    document.getElementById("file-dropdown").onchange = dataListener;
    document.getElementById("projection-dropdown").onchange = projectionListener;
    document.getElementById("width-val").onchange = widthListener;
    document.getElementById("btn-download").addEventListener('click', downloadListener);

    document.getElementById("btn-hide-dht-table").addEventListener('click', dhtTableListener);
})(); // call the async function to execute immediately in asynchronous context
