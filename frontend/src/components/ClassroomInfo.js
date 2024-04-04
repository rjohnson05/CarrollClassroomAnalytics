import {useParams} from "react-router-dom";
import NavBar from "./NavBar";
import axios from "axios";
import React, {useEffect, useState} from "react";
import '../css/ClassroomInfo.css'
import DayCalendar from "./ClassroomDaySchedule";

/**
 * Displays the individual classroom pages, showing the weekly schedule for a single classroom. The times during which
 * the classroom is used are colored. Hovering over these colored blocks shows a tooltip with information about the
 * course taking place in the classroom during that time block.
 *
 * @author Ryan Johnson
 */
export default function ClassroomInfo() {
    const classroomName = useParams().id
    const [timeBlocks, setTimeBlocks] = useState(false);
    const [courseData, setCourseData] = useState(false)

    /*
    Loads the data for a given classroom, including its stats (number of seats, size, etc.) and course schedule. This
    only once when the page first loads.
     */
    useEffect(() => {
        loadData();
    }, []);

    /**
     * Loads the data for a specific classroom, including two dictionaries. the first contains the time block splits for
     * every weekday. A time block is the time period from when a course starts/finishes in the classroom to when any
     * course starts/finishes in the same classroom. This dictionary is used for rendering the visual display of the
     * colored calendar. The second dictionary contains the data about which courses are taking place during each time
     * block, which is used for displaying information in the tooltips.
     */
    const loadData = async () => {
        const classroomData = await axios.get("/api/get_classroom_data/", {params: {classroom: classroomName}});
        setTimeBlocks(classroomData.data[0]);
        setCourseData(classroomData.data[1]);
    }

    return (<div>
            <NavBar/>

            <h1 className="main-title header">{classroomName} DETAILED VIEW</h1>

            <div className="heatmap-container">
                <div className="week-grid">
                    <div className="time-grid">
                        <div className="hour-labels">
                            <p>6 AM</p>
                            <p>7 AM</p>
                            <p>8 AM</p>
                            <p>9 AM</p>
                            <p>10 AM</p>
                            <p>11 AM</p>
                            <p>12 PM</p>
                            <p>1 PM</p>
                            <p>2 PM</p>
                            <p>3 PM</p>
                            <p>4 PM</p>
                            <p>5 PM</p>
                            <p>6 PM</p>
                            <p>7 PM</p>
                            <p>8 PM</p>
                            <p>9 PM</p>
                            <p>10 PM</p>
                            <p>11 PM</p>
                        </div>

                        <div className="hour-lines">
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                            <hr className="hour-line"/>
                        </div>
                    </div>

                    <div className="days-container">
                        <div className="day">
                            <h3 className="day-header">MONDAY</h3>
                            {/* Displays the heatmap for a single day once it has successfully loaded. Until then, only the
                 Loading text is displayed */}
                            {timeBlocks && courseData && (Object.keys(timeBlocks).length > 0 && Object.keys(courseData).length > 0) ?
                                <div className="heatmap">
                                    <DayCalendar day="M" timeBlockList={timeBlocks['M']} courseData={courseData}/>
                                </div> : timeBlocks && courseData ? <p>No course data available</p> : <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">TUESDAY</h3>
                            {timeBlocks && courseData && (Object.keys(timeBlocks).length > 0 && Object.keys(courseData).length > 0) ?
                                <div className="heatmap">
                                    <DayCalendar day="T" timeBlockList={timeBlocks['T']} courseData={courseData}/>
                                </div> : timeBlocks && courseData ? <p>No course data available</p> : <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">WEDNESDAY</h3>
                            {timeBlocks && courseData && (Object.keys(timeBlocks).length > 0 && Object.keys(courseData).length > 0) ?
                                <div className="heatmap">
                                    <DayCalendar day="W" timeBlockList={timeBlocks['W']} courseData={courseData}/>
                                </div> : timeBlocks && courseData ? <p>No course data available</p> : <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">THURSDAY</h3>
                            {timeBlocks && courseData && (Object.keys(timeBlocks).length > 0 && Object.keys(courseData).length > 0) ?
                                <div className="heatmap">
                                    <DayCalendar day="th" timeBlockList={timeBlocks['th']} courseData={courseData}/>
                                </div> : timeBlocks && courseData ? <p>No course data available</p> : <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">FRIDAY</h3>
                            {timeBlocks && courseData && (Object.keys(timeBlocks).length > 0 && Object.keys(courseData).length > 0) ?
                                <div className="heatmap">
                                    <DayCalendar day="F" timeBlockList={timeBlocks['F']} courseData={courseData}/>
                                </div> : timeBlocks && courseData ? <p>No course data available</p> : <p>Loading...</p>}
                        </div>
                    </div>
                </div>
            </div>
        </div>);
}