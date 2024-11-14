// Specify the chart’s dimensions.
const width = 928;
const height = width;
const radius = width / 5;

function drawChart(container, data){
  console.log(data);

  // Create the color scale.
  const color = d3.scaleOrdinal(d3.quantize(d3.interpolateRainbow, data.children.length + 1));

  // Compute the layout.
  const hierarchy = d3.hierarchy(data)
    .sum(d => d.count)
    .sort((a, b) => b.value - a.value);

  const root = d3.partition()
    .size([2 * Math.PI, hierarchy.height + 1])
    (hierarchy);
  root.each(d => d.current = d);

  // Create the arc generator.
  const arc = d3.arc()
    .startAngle(d => d.x0)
    .endAngle(d => d.x1)
    .padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.005))
    .padRadius(radius * 1.5)
    .innerRadius(d => d.y0 * radius)
    .outerRadius(d => Math.max(d.y0 * radius, d.y1 * radius - 1))

  // Create the SVG container.
  const svg = d3.select(container).append('svg')
    .attr("viewBox", [-width / 2, -height / 2, width, width])
    .style("font", "10px sans-serif");
    
  // Append the arcs.
  const path = svg.append("g")
    .selectAll("path")
    .data(root.descendants().slice(1))
    .join("path")
      .attr("fill", d => { while (d.depth > 1) d = d.parent; return color(d.data.name); })
      .attr("fill-opacity", d => arcVisible(d.current) ? (d.children ? 0.6 : 0.4) : 0)
      .attr("pointer-events", d => arcVisible(d.current) ? "auto" : "none")
      .attr("d", d => arc(d.current));

  // Text in center
  const centerText = svg
    .append("text")
    .attr("text-anchor", "middle")
    .attr("fill", "#888")
    .style("visibility", "hidden");

  centerText
    .append("tspan")
    .attr("class", "category")
    .attr("x", 0)
    .attr("y", 0)
    .attr("dy", "-0.5em")
    .attr("font-size", "1.6em")
    .text("")

  centerText
    .append("tspan")
    .attr("class", "count")
    .attr("x", 0)
    .attr("y", 0)
    .attr("dy", "2.2em")
    .attr("font-size", "1.4em")
    .text("");

  // Example prompt text
  const examplePromptText = d3.select(".container #example-text")
    .style("visibility", "hidden");

  // Clickable
  path.style("cursor", "pointer")
    .on("click", function(event, d) {
      if (d.children) {
        clicked(event, d);
      } else {
        console.log('leaf');
        leafClicked(event, d);
      }
    });

  // Hover
  path.on("mouseover", function (event, d) {
    console.log(`Hovered node depth: ${d.depth}, height: ${d.height}`);
    d3.select(this)
        .attr("fill-opacity", 1);

    centerText.style("visibility", null)

    centerText.select(".category")
      .text("Category: " + d.data.name)
      .call(wrap, radius * 3/2);

    const firstLineHeight = centerText.select(".category").node().getBBox().height;
    console.log(`hight: ${firstLineHeight}`);

    centerText.select(".count")
      .attr("dy", `${firstLineHeight + 5}px`)
      .text("Count: " + d.value + " prompts");
  })
  .on("mouseout", function () {
    d3.select(this)
      .attr("fill-opacity", d => arcVisible(d.current) ? (d.children ? 0.6 : 0.4) : 0);
    centerText.style("visibility", "hidden");
  })

  const format = d3.format(",d");
  path.append("title")
    .text(d => `${d.ancestors().map(d => d.data.name).reverse().join("/")}\n${format(d.count)}`);

  const label = svg.append("g")
    .attr("pointer-events", "none")
    .attr("text-anchor", "middle")
    .style("user-select", "none")
    .selectAll("text")
    .data(root.descendants().slice(1))
    .join("text")
    .attr("dy", "0.35em")
    .attr("font-size", d => calculateFontSize(d)) 
    .attr("fill-opacity", d => +labelVisible(d.current))
    .attr("transform", d => labelTransform(d.current))
    .text(d => d.data.name);


  const parent = svg.append("circle")
    .datum(root)
    .attr("r", radius)
    .attr("fill", "none")
    .attr("pointer-events", "all")
    .on("click", clicked);


  // Handle zoom on click.
  function clicked(event, p) {
    examplePromptText
      .text("")
      .style("visibility", "hidden");
    parent.datum(p.parent || root);
    
    root.each(d => d.target = {
      x0: Math.max(0, Math.min(1, (d.x0 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
      x1: Math.max(0, Math.min(1, (d.x1 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
      y0: Math.max(0, d.y0 - p.depth),
      y1: Math.max(0, d.y1 - p.depth)
    });

    const t = svg.transition().duration(750);
    
    // Transition the data on all arcs, even the ones that aren’t visible,
    // so that if this transition is interrupted, entering arcs will start
    // the next transition from the desired position.
    path.transition(t)
        .tween("data", d => {
          const i = d3.interpolate(d.current, d.target);
          return t => d.current = i(t);
        })
      .filter(function(d) {
        return +this.getAttribute("fill-opacity") || arcVisible(d.target);
      })
        .attr("fill-opacity", d => arcVisible(d.target) ? (d.children ? 0.6 : 0.4) : 0)
        .attr("pointer-events", d => arcVisible(d.target) ? "auto" : "none") 

        .attrTween("d", d => () => arc(d.current));
    
    label.filter(function(d) {
        return + this.getAttribute("fill-opacity") || labelVisible(d.target);
      }).transition(t)
        .attr("fill-opacity", d => +labelVisible(d.target))
        .attrTween("transform", d => () => labelTransform(d.current))
        .each(function(d) { 
          if (d.wrapped === undefined) d.wrapped = false;

          if (!d.wrapped) {
              d3.select(this).call(wrap, radius);
              d.wrapped = true;
          }
        });
    
  }

  function leafClicked(event, d) {
    if (d.data.example1 && d.data.example1.length > 0) {
      examplePromptText
        .style("visibility", null) 
        .text(`Example Prompt: ${d.data.example1}`);
    }
  }

  function arcVisible(d) {
    return d.y1 < 3 && d.y0 >= 1 && d.x1 > d.x0;
  }

  function labelVisible(d) {
    return d.y1 < 3 && d.y0 >= 1 && (d.y1 - d.y0) * (d.x1 - d.x0) > 0.05;
  }

  function labelTransform(d) {
    const x = (d.x0 + d.x1) / 2 * 180 / Math.PI;
    const y = (d.y0 + d.y1) / 2 * radius;
    return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`;
  }

  function calculateFontSize(d) {
    const r = (d.y1 + d.y0) / 2 * radius; 
    const angle = (d.x1 - d.x0) * r; 
    const baseFontSize = 10; 
    return Math.min(baseFontSize, angle * 3 / 5); 
  }

  function wrap(text, width) {
    text.each(function() {
      var text = d3.select(this),
        words = text.text().split(/\s+/).reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        y = text.attr("y"),
        dy = parseFloat(text.attr("dy")),
        tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
      while (word = words.pop()) {
        line.push(word);
        tspan.text(line.join(" "));
        if (tspan.node().getComputedTextLength() > width) {
          line.pop();
          tspan.text(line.join(" "));
          line = [word];
          tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
        }
      }
    });
  }
}