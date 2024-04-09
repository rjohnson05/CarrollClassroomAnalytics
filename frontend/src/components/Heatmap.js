import * as d3 from "d3";
import {Tooltip} from 'react-tooltip'
import 'react-tooltip/dist/react-tooltip.css'
import '../css/Heatmap.css'
import {Link} from "react-router-dom";


/**
 * Component to display the number of classrooms in use for each time block during throughout a day. These numbers are
 * coded by color, with time blocks with large number of classrooms in use being represented by a darker purple color and time
 * blocks with fewer classrooms in use being represented by a lighter yellow color. If the time blocks are hovered over by the
 * mouse, a tooltip displays the number of classrooms in use.
 *
 * @param day string specifying which weekday the component should display data for (M, T, W, th, F)
 * @param buildingList list containing the names of each building used for housing courses on the Carroll College campus
 * @param timeBlockList dictionary containing each possible block of time during the day. The keys of this dictionary
 *                      are strings indicating the weekday, and the values are doubly-indexed arrays, with each subarray containing a single
 *                       time block for the day.
 * @param numClassroomsList dictionary holding the data about the number of classrooms used during each time block throughout the week. The keys are
 *                   the start time of the time block, and the values are integers describing the number of classrooms used during that time block.
 * @param maxNumberClasses integer describing the maximum number of classes used during any one time block throughout the week
 *
 * @author Ryan Johnson
 */
export default function Heatmap({day, buildingList, timeBlockList, numClassroomsList, maxNumberClasses}) {
    const colorScale = d3.scaleLinear()
        .domain([0, 1 * maxNumberClasses / 3, 2 * maxNumberClasses / 3, maxNumberClasses])
        .range(['white', '#fcf881', '#eb0000', 'purple'])


    /**
     * Calculates the number of minutes between a start/end time. This is used for forming the size of the colored
     * blocks of the heatmap.
     *
     * @param startTime   String representing the starting time for the block
     * @param endTime     String representing the ending time for the block
     * @returns {number}  Number representing the number of minutes between the start and end time
     */
    const calculateMinutes = (startTime, endTime) => {
        startTime = startTime.split(":");
        endTime = endTime.split(":");
        const minutes = endTime[1] - startTime[1];
        // Accounts for the noonday hour change from 12 to 1
        if ((parseInt(startTime[0]) > 1 && endTime[0] === '1')) {
            return (60 + minutes) / (1.6);
        }
        // Handles all other hour changes
        const hourMinutes = 60 * (endTime[0] - startTime[0]);
        return (hourMinutes + minutes) / 5;
    }


    return (<div>
            {/*A tooltip appears when hovering over the colored blocks, showing how many classrooms are in use*/}
            <Tooltip className="dark" anchorSelect=".tooltip-target" place="right" clickable={true}
                     render={({content}) => {
                         if (content) {
                             const contentParts = content.split(",");
                             const day = contentParts[3];
                             const buildingListArray = Object.entries(buildingList).filter(([key, value]) => key && value)
                                                   .map(([key]) => key).join(', ');
                             const startTime = contentParts[0]?.substring(0, 5);
                             const endTime = contentParts[1]?.substring(0, 5);
                             return (<div style={{display: 'flex', flexDirection: 'column'}}>
                                     <span>Time: {contentParts[0]?.substring(0, 5)} - {contentParts[1]?.substring(0, 5)}</span>
                                     <span>Classrooms in Use: {contentParts[2]}</span>
                                     {/*Link to show which classrooms are used during a specific time block*/}
                                     <Link className="link" to={{pathname: `/used_classrooms`, search: `?day=${day}&buildingList=${buildingListArray}&startTime=${startTime}&endTime=${endTime}`}} target="_blank" rel="noopener noreferrer">
                                         View Used Classrooms</Link>
                                 </div>);
                         } else {
                             return null;
                         }
                     }}></Tooltip>
            {timeBlockList ? timeBlockList.map((timeBlock) => (
                <svg key={timeBlock} viewBox={`0 0 100 ${calculateMinutes(timeBlock[0], timeBlock[1])}`}
                     style={{display: "block"}}>
                    <rect width="100%" height={calculateMinutes(timeBlock[0], timeBlock[1]) + 1}
                          fill={colorScale(numClassroomsList[timeBlock[0]])}
                          className="tooltip-target"
                          data-tooltip-content={[timeBlock[0], timeBlock[1], numClassroomsList[timeBlock[0]], day, buildingList]}/>
                </svg>)) : <p>No heatmap data available</p>}
        </div>);
}