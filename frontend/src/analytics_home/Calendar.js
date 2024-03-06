import React, {useEffect, useState} from "react";
import 'primeicons/primeicons.css'
import axios from "axios";

import './Calendar.css';
import HeatMap from "./Heatmap";
import NavBar from "./NavBar";
import Legend from "./Legend"
import * as d3 from "d3";

/**
 * Displays the main page, showing the number of used classrooms during each time block throughout the week. Allows the
 * user to filter different buildings to view the number of used classrooms in any combination of buildings.
 *
 * @author Ryan Johnson, Adrian Rincon-Jimanez
 */
export default function Home() {
    const [firstRender, setFirstRender] = useState(true);
    const [timeBlocks, setTimeBlocks] = useState(false);
    const [numberClasses, setNumberClasses] = useState(false);
    const [maxNumClasses, setMaxNumClasses] = useState(null);
    const [filterOpen, setFilterOpen] = useState(false);
    const [buildingFilter, setBuildingFilter] = useState({});
    const [buildingNames, setBuildingNames] = useState({});

    useEffect( () => {
        /**
         * Fetches the data detailing the number of classes per time block from the database upon startup, reloading
         * whenever the building filter is changed. Also loads the names of the buildings from the database for use
         * in the buildings filter.
         */
        async function fetchData() {
            await loadData();
            if (firstRender) {
                await loadFilter();
            }
        }
        fetchData();
    }, [buildingFilter]);

    useEffect(() => {
        calculateMaxNumClasses()
    }, [numberClasses]);

    /**
     * Loads the data from the backend. This loads two dictionaries. The first contains the time block divisions, and the
     * second contains the number of classes running during each time block. Both of these dictionaries are stored as state.
     */
    const loadData = async () => {
        try {
            // Creates the list of buildings that are currently selected in the filter, used for querying
            const currentFilter = []
            Object.keys(buildingFilter).forEach(building => {
                if (buildingFilter[building] === true) {
                    currentFilter.push(building)
                }
            })

            // Loads the time blocks for the week and the number of classes for each time block
            const classesData = await axios.get("http://localhost:8000/api/get_number_classes",
                {params: {buildings: currentFilter}});
            setTimeBlocks(classesData.data[0]);
            setNumberClasses(classesData.data[1]);

            // Loads the names of all buildings in the database for use in the filter
            const buildingNamesData = await axios.get("http://localhost:8000/api/get_building_names");
            setBuildingNames(buildingNamesData.data);
        } catch (error) {
            console.error(error);
        }
    }

    /**
     * Calculates the new maximum number of classrooms used within the current building filter, passed to the legend and
     * heatmaps for consistency in color scales. This max is updated whenever the building filter is changed.
     */
    const calculateMaxNumClasses = () => {
        let maxNumberClasses = 0;
        for (let dayClasses of Object.values(numberClasses)) {
            for (let numClasses of Object.values(dayClasses)) {
                if (numClasses > maxNumberClasses) {
                    maxNumberClasses = numClasses;
                }
            }
        }
        setMaxNumClasses(maxNumberClasses);
    }

    /**
     * Fetches the names of all the buildings from the database in which classrooms are located. These names are used
     * for the building filter.
     */
    const loadFilter = async () => {
        const buildingNamesData = await axios.get("http://localhost:8000/api/get_building_names");
            const filter = {}
            Object.keys(buildingNamesData.data).forEach(item => {
                filter[item] = false; // Initialize all filters to false
            });
        setBuildingFilter(filter)
        setFirstRender(false)
    }

    /**
     * Changes the current building filter based on the number of checkboxes the user has checked. This is used for
     * altering the appearance of the heatmaps. The filter data structure is a dictionary containing the name of every
     * building as a key and values indicating whether the building is checked or not. When a box is checked, its
     * corresponding building is set to true in the dictionary, and vice versa.
     *
     * @param building  list of dictionary objects holding the abbreviation for the checked buildings
     */
    const filterBuilding = (building) => {
        setBuildingFilter(prevState => ({
            ...prevState,
            [building['abbrev']]: !prevState[building['abbrev']]
        }));
    }


    return (
        <div className="body">
            <NavBar/>
            <h1 className="main-title header-font">CLASSROOM UTILIZATION OVERVIEW</h1>

            <div className="filter-container">
                <button className="filter-button" onClick={() => {
                    setFilterOpen(!filterOpen)
                }}>
                    <span className="pi pi-filter-fill filter-icon"></span>FILTER
                </button>

                {filterOpen &&
                    <form className="filter-dropdown">
                        {Object.keys(buildingNames).map(abbrev => (
                            <div key={abbrev}>
                                <input type="checkbox" checked={buildingFilter[abbrev]} name={abbrev}
                                       onClick={() => filterBuilding({abbrev})}/>
                                <label className="filter-options" htmlFor={abbrev}>{buildingNames[abbrev]}</label>
                            </div>
                        ))}
                    </form>
                }
            </div>

            <div className="heatmap-container">
                <div className="legend-container">
                    {Object.keys(numberClasses).length > 0 && maxNumClasses ?
                        <Legend className="legend" numClassroomsList={numberClasses} maxNumberClasses={maxNumClasses}/>
                        : 'Legend Loading...'}
                </div>

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
                            {(Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['M']}
                                             day='M' buildingList={buildingFilter} numClassroomsList={numberClasses['M']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div>
                                : <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">TUESDAY</h3>
                            {(Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['T']}
                                             day='T' buildingList={buildingFilter} numClassroomsList={numberClasses['T']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div>
                                : <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">WEDNESDAY</h3>
                            {(Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['W']}
                                             day='W' buildingList={buildingFilter} numClassroomsList={numberClasses['W']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div>
                                : <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">THURSDAY</h3>
                            {(Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['th']}
                                             day='th' buildingList={buildingFilter} numClassroomsList={numberClasses['th']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div>
                                : <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">FRIDAY</h3>
                            {(Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['F']}
                                             day='F' buildingList={buildingFilter} numClassroomsList={numberClasses['F']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div>
                                : <p>Loading...</p>}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}