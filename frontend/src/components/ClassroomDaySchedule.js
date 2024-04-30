import {Tooltip} from 'react-tooltip'
import 'react-tooltip/dist/react-tooltip.css'
import '../css/ClassroomDaySchedule.css'


/**
 * Component to display the course being used during a specific time block during the day. A time block is considered as
 * the period between each course start/end time. This component is similar to the heatmap component shown on the main
 * page, except that only one color is used to show when the classroom contains a course. When a time block is hovered
 * over, a tooltip shows information about the course using the classroom during the time block.
 *
 * @param day string specifying which weekday the component should display data for (M, T, W, th, F)
 * @param timeBlockList dictionary containing each possible block of time during the day. The keys of this dictionary
 *                      are strings indicating the weekday, and the values are doubly-indexed arrays, with each subarray containing a single
 *                       time block for the day.
 * @param courseData dictionary holding the data about all courses using the classroom throughout the week. The keys are
 *                   the start time of the time block, and the values are dictionaries containing the course data
 *                   (including the course name, instructor name, and number of students enrolled).
 *
 * @author Ryan Johnson
 */
export default function ClassroomDaySchedule({day, timeBlockList, courseData}) {
    /**
     * Calculates the number of minutes between a start/end time. This is used for forming the size of the colored/white
     * blocks on the day calendar.
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

    /**
     * Selects the course data for a specific time block. This is used when displaying course data in the tooltip. This
     * course data includes the name, instructors, number of students enrolled, and day of the week. The course name,
     * instructor, and enrollment data are stored in lists. In the case of multiple courses being listed during the same
     * time block, the length of these lists is greater than one.
     *
     * @param timeBlock Array of two strings: the start/end times of the block
     * @returns         Array containing the data for the course being held during the specified time block
     */
    const selectData = (timeBlock) => {
        const startTime = timeBlock[0];
        const endTime = timeBlock[1];
        const courseNameList = []
        const instructorsList = []
        const studentsEnrolledList = []

        for (let i = 0; i < courseData[day][timeBlock[0]].length; i++) {
            courseNameList.push(courseData[day][timeBlock[0]][i][0]);
            instructorsList.push(courseData[day][timeBlock[0]][i][1]);
            studentsEnrolledList.push(courseData[day][timeBlock[0]][i][2]);
        }

        return [startTime, endTime, courseNameList, instructorsList, studentsEnrolledList, day]
    }

    return (<div>
        <Tooltip className="dark" anchorSelect=".tooltip-target" place="right" clickable={true}
                 render={({content}) => {
                     if (content) {
                         const contentsArray = JSON.parse(content);
                         const startTime = contentsArray[0];
                         const endTime = contentsArray[1];
                         const courseNameList = contentsArray[2];
                         const instructorsList = contentsArray[3];
                         const studentsEnrolledList = contentsArray[4];

                         return (<div style={{display: 'flex', flexDirection: 'column'}}>
                             <span>Time: {startTime?.substring(0, 5)} - {endTime?.substring(0, 5)}</span>
                             {console.log(courseNameList[0])}
                             {courseNameList[0] !== null ?
                                 courseNameList.map((courseName, index) => (
                                     <div>
                                         <hr/>
                                         <p className="tooltip-line">Course: {courseNameList[index]}</p>
                                         <p className="tooltip-line">Instructor: {instructorsList[index]}</p>
                                         <p className="tooltip-line">Students
                                             Enrolled: {studentsEnrolledList[index]}</p>
                                     </div>)) :
                                 <div>
                                     <hr/>
                                     <p className="tooltip-line">Course: N/A</p>
                                     <p className="tooltip-line">Instructor: N/A</p>
                                     <p className="tooltip-line">Students Enrolled: N/A</p>
                                 </div>}
                         </div>);
                     } else {
                         return null;
                     }
                 }}></Tooltip>
        {timeBlockList ? timeBlockList.map((timeBlock) => (
            <svg key={timeBlock} viewBox={`0 0 100 ${calculateMinutes(timeBlock[0], timeBlock[1])}`}
                 style={{display: "block"}}>
                <rect width="100%" height={calculateMinutes(timeBlock[0], timeBlock[1]) + 1}
                      fill={courseData[day][timeBlock[0]][0][0] === undefined ? "#ffffff" : "#cfb988"}
                      className="tooltip-target"
                      data-tooltip-content={JSON.stringify(selectData(timeBlock))}/>
            </svg>)) : <p>No classroom data available</p>}
    </div>);
}