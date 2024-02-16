import React, {useEffect, useState} from "react";
import axios from "axios";

import './Calendar.css';
import HeatMap from "./Heatmap";

export default function Home() {
    const [timeBlocks, setTimeBlocks] = useState();
    const [numberClasses, setNumberClasses] = useState();
    const [classDataLoaded, setClassDataLoaded] = useState(false);

    useEffect(async () => {
        loadData();
    }, []);

    /**
     * Loads the data from the backend. This loads two dictionaries. The first contains the time block divisions, and the
     * second contains the number of classes running during each time block. Both of these dictionaries are stored as state.
     */
    const loadData = async () => {
        try {
            const classesData = await axios.get("http://localhost:8000/api/get_number_classes");
            setTimeBlocks(classesData.data[0]);
            setNumberClasses(classesData.data[1]);
            setClassDataLoaded(true);
        } catch (error) {
            console.error(error);
        }
    }


    return (
        <div>
            <h1 className="main-title">Overall Classroom Utilization</h1>
            <div className="days-container">
                <div className="day">
                    <h3 className="day-header">Monday</h3>
                    {/* Displays the heatmap for a single day once it has successfully loaded. Until then, only the
                     Loading text is displayed */}
                    {classDataLoaded ?
                        <HeatMap className="heatmap" timeBlockList={timeBlocks['M']}
                                 numClassroomsList={numberClasses['M']}/> :
                        <p>Loading...</p>}
                </div>
                <div className="day">
                    <h3 className="day-header">Tuesday</h3>
                    <div className="heat-map">Heat Map</div>
                </div>
                <div className="day">
                    <h3 className="day-header">Wednesday</h3>
                    <div className="heat-map">Heat Map</div>
                </div>
                <div className="day">
                    <h3 className="day-header">Thursday</h3>
                    <div className="heat-map">Heat Map</div>
                </div>
                <div className="day">
                    <h3 className="day-header">Friday</h3>
                    <div className="heat-map">Heat Map</div>
                </div>
            </div>
        </div>
    )
}