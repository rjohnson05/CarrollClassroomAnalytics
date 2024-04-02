import { Tooltip } from 'react-tooltip'
import 'react-tooltip/dist/react-tooltip.css'
import '../css/DayCalendar.css'


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
export default function DayCalendar({ day, timeBlockList, courseData }) {
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
            <Tooltip className="dark" anchorSelect=".tooltip-target" place="right" clickable={true} render={({content}) => {
                if (content) {
                    const contentParts = content.split(",");
                    return (
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span>Time: {contentParts[0]?.substring(0,5)} - {contentParts[1]?.substring(0,5)}</span>
                            {contentParts[2] !== "" ?
                                <div>
                                    <p className="tooltip-line">Course: {contentParts[2]}</p>
                                    <p className="tooltip-line">Instructor: {contentParts[3]}</p>
                                    <p className="tooltip-line">Students Enrolled: {contentParts[4]}</p>
                                </div> :
                                <div>
                                    <p className="tooltip-line">Course: N/A</p>
                                    <p className="tooltip-line">Instructor: N/A</p>
                                    <p className="tooltip-line">Students Enrolled: N/A</p>
                                </div>
                            }
                        </div>
                    );
                } else {
                    return null;
                }
            }}></Tooltip>
            {timeBlockList ?
                timeBlockList.map((timeBlock) => (
                    <svg key={timeBlock} viewBox={`0 0 100 ${calculateMinutes(timeBlock[0], timeBlock[1])}`}
                         style={{display: "block"}}>
                        <rect width="100%" height={calculateMinutes(timeBlock[0], timeBlock[1]) + 1}
                              fill={courseData[day][timeBlock[0]][0][0] === undefined ? "#ffffff" : "#cfb988"}
                              className="tooltip-target" data-tooltip-content={[timeBlock[0], timeBlock[1],
                            courseData[day][timeBlock[0]][0][0], courseData[day][timeBlock[0]][0][1],
                            courseData[day][timeBlock[0]][0][2], day]} />
                    </svg>
                )) : <p>No classroom data available</p>}
        </div>
    );
}