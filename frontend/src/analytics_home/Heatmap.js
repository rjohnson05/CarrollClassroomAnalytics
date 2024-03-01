import * as d3 from "d3";
import { Tooltip } from 'react-tooltip'
import 'react-tooltip/dist/react-tooltip.css'
import './Heatmap.css'


/**
 * Component to display the number of classrooms in use for each time block during throughout a day. These numbers are
 * coded by color, with time blocks with large number of classrooms in use being represented by a darker color and time
 * blocks with less classrooms in use being represented by a lighter color. If the time blocks are hovered over by the
 * mouse, a tooltip displays the number of classrooms in use.
 *
 * @param timeBlockList dictionary containing each possible block of time during the day
 * @param numClassroomsList dictionary containing the number of classrooms used during each time block throughout the day
 *
 * @author Ryan Johnson
 */
export default function Heatmap({ timeBlockList, numClassroomsList, maxNumberClasses }) {
    const colorScale = d3.scaleLinear()
        .domain([0, 1*maxNumberClasses / 3, 2 *maxNumberClasses / 3,  maxNumberClasses])
        .range(['white', '#fcf881', '#eb0000', 'purple'])

    /**
     * Calculates the number of minutes between a start and end time for display purposes.
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
            return (60 + minutes)/(1.6);
        }
        // Handles all other hour changes
        const hourMinutes = 60*(endTime[0] - startTime[0]);
        return (hourMinutes + minutes)/5;
    }


    return (
        <div>
            <Tooltip className="dark" anchorSelect=".tooltip-target" place="right" render={({content}) => {
                if (content) {
                    const contentParts = content.split(",");
                    return (
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span>Time: {contentParts[0]?.substring(0,5)} - {contentParts[1]?.substring(0,5)}</span>
                            <span>Classrooms in Use: {contentParts[2]}</span>
                        </div>
                    );
                } else {
                    return null;
                }
            }}></Tooltip>
            {timeBlockList ?
                timeBlockList.map((timeBlock) => (
                    <svg viewBox={`0 0 100 ${calculateMinutes(timeBlock[0], timeBlock[1])}`}
                         style={{display: "block"}}>
                        <rect width="100%" height={calculateMinutes(timeBlock[0], timeBlock[1]) + 1}
                              fill={colorScale(numClassroomsList[timeBlock[0]])}
                              className="tooltip-target" data-tooltip-content={[timeBlock[0], timeBlock[1], numClassroomsList[timeBlock[0]]]} />
                    </svg>
                )) : <p>No heatmap data available</p>}
        </div>
    );
}