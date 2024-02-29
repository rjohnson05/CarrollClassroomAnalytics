import React, {useEffect, useRef} from "react";
import * as d3 from "d3";

/**
 * Creates the legend on the main page for showing how many classrooms are in use during a specific time block during the day.
 * Takes a dictionary containing the number of classrooms occupied during each time block during the week to adjust the
 * scaling for the colors.
 *
 * @param numClassroomsList dictionary containing the number of classrooms occupied during each time block during the week
 * @returns {Element} svg image containing the legend with a title and x-axis
 * @author Ryan Johnson
 */
export default function Legend({numClassroomsList}) {
    const svgRef = React.useRef(null);
    const numClasses = Object.values(numClassroomsList);

    const margin = {top: 20, bottom: 10, left: 5, right: 4};
    const width = 400;
    const height = 50;

    useEffect(() => {
        // Creates the base image
        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();
        svg.append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        // Creating the x-axis
        const xScale = d3.scaleLinear()
            .domain([0, Math.max(...numClasses)])
            .range([margin.left, width]);
        const xAxisGenerator = d3.axisBottom(xScale)
            .ticks(5)
            .tickSize(0)
        svg.append("g")
            .call(xAxisGenerator)
            .attr("transform",`translate(${0}, ${height + margin.top})`)

        // Creates the color range for the legend
        const colors = ['white','#fcf881', '#eb0000', 'purple']
        const colorRange = d3.range(0, 1, 1.0 / (colors.length - 1))
        colorRange.push(1)

        // Constructs the color gradient
        const defs = svg.append("defs");
        const linearGradient = defs.append("linearGradient")
            .attr("id", "linear-gradient")
            .attr("x1", "0%")
            .attr("y1", "0%")
            .attr("x2", "100%")
            .attr("y2", "0%");

        colors.forEach((color, i) => {
            linearGradient.append("stop")
                .attr("offset", `${colorRange[i] * 100}%`)
                .attr("stop-color", color);
        });

        // Creating the rectangle for the colors
        svg.append("rect")
            .attr("width", width)
            .attr("height", height)
            .attr("x", margin.left)
            .attr("y", margin.top)
            .attr("fill", "url(#linear-gradient)")

        // Adding the title
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", 3*margin.top/4)
            .attr("text-anchor", "middle")
            .attr("font-weight", "bold")
            .text("Number of Classrooms Used");
    }, [numClassroomsList]);

    return <svg ref={svgRef} width={width + margin.left + margin.right} height={height + margin.top + margin.bottom} />;
}
