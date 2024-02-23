import React, {useEffect, useState} from "react";
import {Box, Button, Fab} from "@mui/material";
import axios from "axios";

import './Calendar.css';
import HeatMap from "./Heatmap";
import NavBar from "./NavBar";
import FilterAltIcon from '@mui/icons-material/FilterAlt';
import Filter from "./Filter";

export default function Home() {
    const [timeBlocks, setTimeBlocks] = useState();
    const [numberClasses, setNumberClasses] = useState();
    const [classDataLoaded, setClassDataLoaded] = useState(false);

    useEffect( () => {
        async function fetchData() {
            const response = await loadData();
        }
        fetchData();
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
            <NavBar />
            <h1 className="main-title header-font">CLASSROOM UTILIZATION OVERVIEW</h1>
            <Fab variant="extended" size="medium" color="primary" sx={{
                backgroundColor: '#cfb988',
                color: '#4a4644',
                fontWeight: 'bold',
                '&:hover': {
                    backgroundColor: "#bfaa7a"
                },}}
                 className="filter">
                <FilterAltIcon/>
                FILTER
            </Fab>
            <Filter></Filter>
            <div className="days-container">
                <div className="day">
                    <h3 className="day-header">MONDAY</h3>
                    {/* Displays the heatmap for a single day once it has successfully loaded. Until then, only the
                     Loading text is displayed */}
                    {classDataLoaded ?
                        <HeatMap className="heatmap" timeBlockList={timeBlocks['M']}
                                 numClassroomsList={numberClasses['M']}/> :
                        <p>Loading...</p>}
                </div>
                <div className="day">
                    <h3 className="day-header">TUESDAY</h3>
                    <div className="heat-map">Heat Map</div>
                </div>
                <div className="day">
                    <h3 className="day-header">WEDNESDAY</h3>
                    <div className="heat-map">Heat Map</div>
                </div>
                <div className="day">
                    <h3 className="day-header">THURSDAY</h3>
                    <div className="heat-map">Heat Map</div>
                </div>
                <div className="day">
                    <h3 className="day-header">FRIDAY</h3>
                    <div className="heat-map">Heat Map</div>
                </div>
            </div>
        </div>
    )
}