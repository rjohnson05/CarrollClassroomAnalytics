import {useEffect, useState} from "react";
import Popup from "reactjs-popup";

export default function HeatMap({ timeBlockList, numClassroomsList }) {
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
        const hours = 60*(endTime[0] - startTime[0]);
        return (hours + minutes)/(1.7);
    }

    /**
     * Calculates the shade color for a time block based on the number of classrooms being utilized during that
     * particular block. Lighter color shades indicate less utilized classrooms, while darker shades indicate a greater
     * number of classrooms being used.
     *
     * @param numberClasses Number representing the number of classrooms being actively used during a particular time
     *                      period
     * @returns {string}    String representing the color to be assigned to the time block
     */
    const calculateColor = (numberClasses) => {
        if (numberClasses === 0) {
            return 'white';
        } else if (numberClasses <= 5) {
            return '#e7d87d';
        } else if (numberClasses <= 10) {
            return '#dd9f40';
        } else if (numberClasses <= 20) {
            return '#b4451f';
        } else if (numberClasses > 20) {
            return '#b01111';
        }
    }


    return (
        <div>
            {timeBlockList ?
            timeBlockList.map((timeBlock) => (
                <Popup trigger={
                    <div className="time-block" style={{
                        border: '1px solid black',
                        height: calculateMinutes(timeBlock[0], timeBlock[1]),
                        background: calculateColor(numClassroomsList[timeBlock[0]])}}>
                    </div>}
                       className="popup-content popup-arrow popup-overlay"
                       position="right center"
                       on={['hover', 'focus']}>
                    <div><p className="popup-title">Classrooms in Use:</p> {numClassroomsList[timeBlock[0]]}</div>
                </Popup>
                )) : <p>No heatmap data available</p>}
        </div>

    );
}