import * as d3 from "d3";
import { Tooltip } from 'react-tooltip'
import 'react-tooltip/dist/react-tooltip.css'
import './Heatmap.css'
import {Link} from "react-router-dom";
// import calculate_number_classes from services.py
import React, {useState} from "react";
import axios from "axios";



/**
 * Component to display the number of classrooms in use for each time block during throughout a day. These numbers are
 * coded by color, with time blocks with large number of classrooms in use being represented by a darker color and time
 * blocks with less classrooms in use being represented by a lighter color. If the time blocks are hovered over by the
 * mouse, a tooltip displays the number of classrooms in use.
 *
 * @param timeBlockList dictionary containing each possible block of time during the day
 * @param numClassroomsList dictionary containing the number of classrooms used during each time block throughout the day
 *
 * @author Adrian Rincon Jimenez
 */


export default function Table({ day, buildingList, timeBlockList, numClassroomsList, numberClasses }) {

    const [numberClassrooms, setNumberClassrooms] = useState(null);

    /**
     * Calculates the number of minutes between a start and end time for display purposes.
     *
     * @param startTime   String representing the starting time for the block
     * @param endTime     String representing the ending time for the block
     * @returns {number}  Number representing the number of minutes between the start and end time
     */

    const load_data = ()=>{
        const load = axios.get('/api/get_number_classes/')
        setNumberClassrooms(load.data)
    }

    return (
        <table className="table" style={{minWidth: '50rem'}}>
            <thead>
            <tr>
                <th>Time</th>
                <th>Monday</th>
                <th>Tuesday</th>
                <th>Wednesday</th>
                <th>Thursday</th>
                <th>Friday</th>
            </tr>
            </thead>
            <tbody>
        {timeBlockList['M'].map((timeBlock, i) => timeBlock ?
            <tr key={timeBl
                ock.join(' ')}>
                <td>{timeBlock.join(' ')}</td>
                <td>{numberClassrooms}</td>
                <td>{numberClasses}</td>
                <td>{numberClasses}</td>
                <td>{numberClasses}</td>
                <td>{numberClasses}</td>
            </tr>
            : <p key={i}> Not showing </p>
        )}
            </tbody>
        </table>


    )

}