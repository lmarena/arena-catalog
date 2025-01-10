function drawChart(data, examples){
    const width = 1600;
    const height = 2 * width / 3;
    const radius = width / 7;
  
    // Create the color scale.
    const color = d3.scaleOrdinal(d3.quantize(d3.interpolateRainbow, data.children.length + 1));
  
    // Compute the layout.
    const hierarchy = d3.hierarchy(data)
        .sum(d => d.count)
        .sort((a, b) => b.value - a.value);
    
    hierarchy.eachAfter(d => {
      if (d.children) {
        d.data.percent = d.children.reduce((sum, child) => sum + (child.data.percent || 0), 0);
      }
      });
  
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
    const svg = d3.select(".chart").append('svg')
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .style("font", "10px Poppins");
    
    // Append the arcs.
    const path = svg.append("g")
      .selectAll("path")
      .data(root.descendants().slice(1))
      .join("path")
        .attr("fill", d => { while (d.depth > 1) d = d.parent; return color(d.data.name); })
        .attr("fill-opacity", d => arcVisible(d.current) ? (d.children ? 0.6 : 0.4) : 0)
        .attr("pointer-events", d => arcVisible(d.current) ? "auto" : "none")
        .attr("d", d => arc(d.current));
    
    // Clickable
    let lastClicked = null; // Track the last clicked data
    var moved = false;
    path.style("cursor", "pointer")
      .on("click", function(event, d) {
        if (d.children) {
          if (!isSmallScreen() || lastClicked === d) {
            moved = false;
            clicked(event, d);
          } else if (isSmallScreen()) {
            showSmallScreenCap();
          }
        } else {
          if (!isSmallScreen() || lastClicked === d) {
            hideSmallScreenCap();
            leafClicked(event, d);
            moved = true;
          } else if (isSmallScreen()) {
            showSmallScreenCap();
          }
        }
        lastClicked = d;
      });
  
    // Hover
    path.on("mouseover", function (event, d) {
      console.log("hovered", d.data.name)
      d3.select(this)
        .attr("fill-opacity", 1);
      d3.select("#category")
        .text(`${d.data.name}`);
        d3.select("#category-small")
        .text(`${d.data.name}`);
      d3.select("#count")
        .text(`${d.value + " prompts"}`)
      d3.select("#count-small")
        .text(`${d.value + " prompts"}`)
      d3.select("#percent")
        .text(() => {
          const value = Math.round(d.data.percent * 10000) / 100;
          return value < 0.01 ? "less than 1%" : value + "%";
        });
      d3.select("#percent-small")
        .text(() => {
          const value = Math.round(d.data.percent * 10000) / 100;
          return value < 0.01 ? "less than 1%" : value + "%";
        });
      d3.select("#undo").style("visibility", "hidden");
    })
    .on("mouseout", function (event, d) {
      d3.select(this)
        .attr("fill-opacity", d => arcVisible(d.current) ? (d.children ? 0.6 : 0.4) : 0);
      d3.select("#category")
        .text("");
      d3.select("#count")
        .text("");
      d3.select("#percent")
        .text("");
      if (d.depth !== 1 && !moving) {
        d3.select("#undo").style("visibility", "visible");
      }
    })
    
    const format = d3.format(",d");
    path.append("title")
        .text(d => `${d.ancestors()
        .map(d => d.data.name).reverse().join("/")}\n${format(d.count)}`);
  
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
        .attr("fill", "light-dark(black, white)")
        .text(d => d.data.name);
    
    const parent = svg.append("circle")
        .datum(root)
        .attr("r", radius)
        .attr("fill", "none")
        .attr("pointer-events", "all")
        .on("click", clicked);
    
    // Handle zoom on click.
    function clicked(event, p) {
      const chartContainer = d3.select(".chart-container");
      const infoContainer = d3.select(".info-container");
  
      // Reset positions
      chartContainer.classed("shift", false);
      infoContainer.classed("visible", false);
  
      d3.select(".info-container").style("visibility", "hidden");
      d3.select(".center-text").style("visibility", "hidden");
      hideSmallScreenCap();
      d3.select("#discription").style("visibility", "visible");
      d3.select("#undo").style("visibility", "hidden");
      d3.select("#prompt").text("");
  
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
          .attrTween("d", d => () => arc(d.current))
          .on("end", function() {
            if (p.depth !== 0) {
              d3.select("#undo").style("visibility", "visible");
            } else {
              d3.select("#undo").style("visibility", "hidden");
            }
          });
  
      label.filter(function(d) {
          return + this.getAttribute("fill-opacity") || labelVisible(d.target);
        }).transition(t)
          .attr("fill-opacity", d => +labelVisible(d.target))
          .attrTween("transform", d => () => labelTransform(d.current))
          .each(function(d) { 
              if (d.wrapped === undefined) d.wrapped = false;
              
              if (!d.wrapped) {
                  d3.select(this).call(wrap, 8/9 * radius);
                  d.wrapped = true;
              }
          });
      
      t.attr("transform", `translate(0, 0)`).on("end", () => {
          d3.select(".center-text").style("visibility", "visible");
          d3.select("#undo").style("visibility", "visible");
      });
    }
  
    var moving = false;
    function leafClicked(event, d) {
        const chartContainer = d3.select(".chart-container");
        const infoContainer = d3.select(".info-container");
        const exampleContainer = document.querySelector(".ex-prompt-container");
        if (exampleContainer) {
          exampleContainer.scrollTop = 0;
        }

        if (!moved) {
            moving = true;
            d3.select(".center-text").style("visibility", "hidden");
            hideSmallScreenCap();
            d3.select("#discription").style("visibility", "hidden");
    
            // Shift the chart to the left and show info-container
            chartContainer.classed("shift", true);
            infoContainer.classed("visible", true);
    
            svg.transition()
                .duration(750)
                .on("end", () => {
                    moving = false;
                    randomExamplePrompts(d);
                    d3.select("#undo").style("visibility", "visible");
                });
        } else {
            randomExamplePrompts(d);
        }
    }
    
    function randomExamplePrompts(d) {
      const prompts = examples.find(b => b.id === d.data.id)?.examples || [];
      const selectedPrompts = prompts.sort(() => 0.5 - Math.random()).slice(0, 5);
  
      d3.select(".example-list").selectAll("li").remove();
      
      selectedPrompts.forEach((example, index) => {
        d3.select(".example-list")
          .append("li")
          .attr("class", "example-item")
          .text(`Ex ${index + 1}: ${example}`);
      });
      d3.select(".center-text").style("visibility", "visible");
      d3.select("#selected-cat")
        .text(`${d.data.name}`);
      d3.select("#selected-count")
        .text(`${"Number of prompts: " + d.data.count}`);
      d3.select(".info-container").style("visibility", "visible");
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
      const baseFontSize = 16; 
      return Math.min(baseFontSize, angle * 1/2); 
    }
  
    function wrap(text, width) {
      text.each(function() {
        var text = d3.select(this),
            words = text.text().split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 1.1,
            y = text.attr("y"),
            dy = parseFloat(text.attr("dy")),
            tspan = text.text(null).append("tspan")
              .attr("x", 0).attr("y", y).attr("dy", dy + "em");
        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
              line.pop();
              tspan.text(line.join(" "));
              line = [word];
              tspan = text.append("tspan")
                .attr("x", 0).attr("y", y)
                .attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
          }
        }
      });
    }

    function isSmallScreen() {
      return window.matchMedia("(max-width: 768px)").matches;
    }

    function showSmallScreenCap() {
      d3.select(".center-text-small").style("max-height", "100%");
      d3.select(".center-text-small").style("max-width", "70vw");
      d3.select(".center-text-small").style("visibility", "visible");
    }

    function hideSmallScreenCap() {
      d3.select(".center-text-small").style("visibility", "hidden");
      d3.select(".center-text-small").style("max-width", "0");
      d3.select(".center-text-small").style("max-height", "0");
    }
  }
  
  