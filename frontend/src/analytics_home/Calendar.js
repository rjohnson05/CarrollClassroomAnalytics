import React, {useEffect, useState} from "react";
import axios from "axios";

import './Calendar.css';
import HeatMap from "./Heatmap";

export default function Home() {
    const [classData, setClassData] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        // Loads the data from the backend upon the page's initial loading
        try {
            // const response = await axios.get("http://localhost:8000/api")
            // setData(response.data)
            setClassData([[5,4,8,7,1],[1,5,4,7,8],[1,4,8,5,6],[1,0,2,5,8],[4,7,8,5,2]])
        } catch (error) {
            console.error(error)
        }
    };

    return (
        <div>
            <h1 className="main-title">Overall Classroom Utilization</h1>
            <div className="days-container">
                <div className="day">
                    <h3 className="day-header">Monday</h3>
                    <HeatMap className="heatmap" timeBlockList={[['7:30','8:00'],['8:00','8:45'],['8:45','8:50'],['8:50','9:00'],
                        ['9:00','9:50'],['9:50','10:00'],['10:00','10:50'],['10:50','11:00'],['11:00','11:50'],
                        ['11:50','12:00'],['12:00','12:50'],['12:50','1:00'],['1:00','1:50'],['1:50','2:00'],
                        ['2:00','2:15'],['2:15','2:50'],['2:50','3:00'],['3:00','3:30'],['3:30','3:45'],['3:45','3:50'],
                        ['3:50','4:00'],['4:00','4:50'],['4:50','5:00'],['5:00','5:50'],['5:50','6:00'],['6:00','6:30'],
                        ['6:30','6:45'],['6:45','8:00'],['8:00','9:00']]}/>
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