import React, { useEffect, useState } from "react";
import axios from "axios";

import './Calendar.css';
import HeatMap from "./Heatmap";

export default function Home() {
    const [timeBlocks, setTimeBlocks] = useState();
    const [numberClasses, setNumberClasses] = useState();
    const [classDataLoaded, setClassDataLoaded] = useState(false);
    const [file, setFile] = useState()

    useEffect(() => {
        loadData();
    }, []);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setFile(file);

        const reader = new FileReader();
        reader.onloadend = () => {
            const csv = reader.result;
            console.log(csv); // You can process the CSV data here
        };
        reader.readAsText(file);
    };

    const handleOnSubmit = (event) => {
        event.preventDefault();
        if (file) {
            const reader = new FileReader();
            reader.onload = function (event) {
                const csvOutput = event.target.result;
            };
            reader.readAsText(file);
        }
    };

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

            {/* File Picker */}
            <input type="file" accept=".csv" id="picker" onChange={handleFileChange}/>
            <button onClick={handleOnSubmit}>Import File</button>

            <div className="days-container">
                <div className="day">
                    <h3 className="day-header">Monday</h3>
                    {/* Displays the heatmap for a single day once it has successfully loaded. Until then, only the
                        Loading text is displayed */}
                    {classDataLoaded ?
                        <HeatMap className="heatmap" timeBlockList={timeBlocks['M']} numClassroomsList={numberClasses['M']}/> :
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
    );
}