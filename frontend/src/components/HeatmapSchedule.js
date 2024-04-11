import React, {useEffect, useRef, useState} from "react";
import 'primeicons/primeicons.css'
import axios from "axios";

import '../css/HeatmapSchedule.css';
import HeatMap from "./Heatmap";
import NavBar from "./NavBar";
import Legend from "./Legend"

/**
 * Displays the main page, showing a heat map to illustrate the number of used classrooms during each time block
 * throughout the week. Each block of time is given a color depending upon the number of classrooms being used during
 * that time block. Darker purple indicates blocks where more classrooms are used, while lighter yellow colors indicate
 * less classroom usage. The user is able to filter different buildings to view the number of used classrooms in any
 * combination of buildings. Hovering over any one of these time blocks shows a tooltip displaying the number of
 * classrooms in use as well as a link to view each classroom being used during the selected (or hovered over) time block.
 *
 * @author Ryan Johnson, Adrian Rincon Jimenez
 */
export default function HeatmapSchedule() {
    const [firstRender, setFirstRender] = useState(true);
    const [timeBlocks, setTimeBlocks] = useState(false);
    const [numberClasses, setNumberClasses] = useState(false);
    const [maxNumClasses, setMaxNumClasses] = useState(null);
    const [filterOpen, setFilterOpen] = useState(false);
    const [buildingFilter, setBuildingFilter] = useState({});
    const [buildingNames, setBuildingNames] = useState({});
    const filterButtonRef = useRef(null);
    const filterDropdownRef = useRef(false);

    /*
    Adds a mouse listener to the whole page for closing the filter with a click outside the filter. This listener is
    reset whenever the filter is opened.
     */
    useEffect(() => {
        document.addEventListener('mousedown', toggleFilter);

        return () => {
            document.removeEventListener('mousedown', toggleFilter);
        };
    }, [filterOpen]);

    // Reloads the data for the heatmaps whenever the building filter is changed.
    useEffect(() => {
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

    /*
    Reloads the maximum number of classes currently displayed, based upon the building filter selection. This number
    impacts the color scale of the heatmaps.
     */
    useEffect(() => {
        calculateMaxNumClasses()
    }, [numberClasses]);

    /**
     * Loads the classroom and building data from the database. The classroom data is stored within two dictionaries:
     * the first contains the time block divisions for the selected buildings, and the second contains the number of
     * classes running during each time block. Both of these dictionaries is used for heatmap display, showing the
     * number of classrooms used during each time block. The building data is used for displaying the building filter.
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
            const classesData = await axios.get("/api/get_number_classes", {params: {buildings: currentFilter}});
            setTimeBlocks(classesData.data[0]);
            setNumberClasses(classesData.data[1]);

            // Loads the names of all buildings in the database for use in the filter
            const buildingNamesData = await axios.get("/api/get_building_names");
            // Add an empty selection to the BUILDINGS dict for selecting/deselecting all building boxes at once
            buildingNamesData.data[""] = "SELECT ALL"
            // Don't allow a filter for off-campus classes, since these have no classrooms at Carroll
            delete buildingNamesData.data["OFCP"]
            setBuildingNames(buildingNamesData.data);
        } catch (error) {
            console.error(error);
        }
    }

    /**
     * Calculates the maximum number of classrooms used within the current building selection. This is passed to the
     * legend and heatmaps for consistency in color scales. This number is updated whenever the building filter is changed.
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
     * Fetches the names of all the building names from the database. These names are used for the building filter.
     */
    const loadFilter = async () => {
        const buildingNamesData = await axios.get("/api/get_building_names");
        const filter = {}
        Object.keys(buildingNamesData.data).forEach(item => {
            filter[item] = false; // Initialize all filters to false
        });
        setBuildingFilter(filter)
        setFirstRender(false)
    }

    /**
     * Changes the current building filter based on the checkboxes the user has checked. This filter is used for
     * altering the appearance of the heatmaps, showing only classroom data for the selected buildings. The filter data
     * structure is a dictionary containing the name of every building as a key and values indicating whether the
     * building is checked or not. When a box is checked, its corresponding building is set to true in the dictionary,
     * and vice versa.
     *
     * @param building  list of dictionary objects holding the abbreviation for the checked buildings
     */
    const filterBuilding = (building) => {
        // Handle the SELECT ALL filter option by setting all buildings to true if none are currently selected and false
        // if at least one other building is selected
        if (building.abbrev === "") {
            const tempBuildingFilter = {};
            if (Object.values(buildingFilter).includes(true)) {
                // Deselect all building checkboxes
                for (let key of Object.keys(buildingFilter)) {
                    tempBuildingFilter[key] = false;
                }
            } else {
                // Select all building checkboxes
                for (let key of Object.keys(buildingFilter)) {
                    tempBuildingFilter[key] = true;
                }
            }
            setBuildingFilter(tempBuildingFilter)
        } else {
            // Handle if a building checkbox is selected/deselected
            setBuildingFilter(prevState => ({
                ...prevState, [building['abbrev']]: !prevState[building['abbrev']]
            }));
        }
    }

    /**
     * Opens and closes the buildings filter. Clicking the "Filter" button toggles the dropdown on and off. Clicking outside
     * the dropdown box closes the filter.
     *
     * @param e Event storing the mouse click
     */
    const toggleFilter = (e) => {
        if (filterButtonRef.current.contains(e.target)) {
            // Open the filter when the button is clicked
            setFilterOpen(!filterOpen);
        } else if (filterOpen && !filterDropdownRef.current.contains(e.target)) {
            // Close the filter if an area outside the filter box or button is clicked
            setFilterOpen(false);
        }
    }


    return (<div className="body">
            <NavBar/>
            <h1 className="main-title header-font">CLASSROOM UTILIZATION OVERVIEW</h1>

            <div className="filter-container">
                <button className="filter-button" ref={filterButtonRef}>
                    <span className="pi pi-filter-fill filter-icon"></span>FILTER
                </button>

                {filterOpen && <form className="filter-dropdown" ref={filterOpen ? filterDropdownRef : false}>
                    {Object.keys(buildingNames).map(abbrev => (<div key={abbrev}>
                            <input type="checkbox" checked={buildingFilter[abbrev]} name={abbrev}
                                   onClick={() => filterBuilding({abbrev})}/>
                            <label className="filter-options" htmlFor={abbrev}>{buildingNames[abbrev]}</label>
                        </div>))}
                </form>}
            </div>

            <div className="heatmap-container">
                <div className="legend-container">
                    {numberClasses && Object.keys(numberClasses).length > 0 && maxNumClasses ?
                        <Legend className="legend" numClassroomsList={numberClasses}
                                maxNumberClasses={maxNumClasses}/> : numberClasses ? "No data available" : "Legend Loading..."}
                </div>

                <div className="week-grid">
                    <div className="time-grid">
                        <div className="hour-block">
                            <p className="hour-label"> 6 AM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label"> 7 AM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label"> 8 AM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label"> 9 AM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label">10 AM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label">11 AM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label">12 PM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label"> 1 PM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label"> 2 PM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label"> 3 PM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label"> 4 PM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label"> 5 PM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label"> 6 PM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label"> 7 PM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label"> 8 PM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label"> 9 PM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label">10 PM</p>
                            <hr className="hour-line"/>
                        </div>
                        <div className="hour-block">
                            <p className="hour-label">11 PM</p>
                            <hr className="hour-line"/>
                        </div>
                    </div>

                    <div className="days-container">
                        <div className="day">
                            <h3 className="day-header">MONDAY</h3>
                            {/* Displays the heatmap for a single day once it has successfully loaded. Until then, only the
                 Loading text is displayed */}
                            {timeBlocks && numberClasses && (Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['M']}
                                             day='M' buildingList={buildingFilter}
                                             numClassroomsList={numberClasses['M']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div> : timeBlocks && numberClasses ? <p>No heatmap data available</p> :
                                    <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">TUESDAY</h3>
                            {timeBlocks && numberClasses && (Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['T']}
                                             day='T' buildingList={buildingFilter}
                                             numClassroomsList={numberClasses['T']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div> : timeBlocks && numberClasses ? <p>No heatmap data available</p> :
                                    <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">WEDNESDAY</h3>
                            {timeBlocks && numberClasses && (Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['W']}
                                             day='W' buildingList={buildingFilter}
                                             numClassroomsList={numberClasses['W']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div> : timeBlocks && numberClasses ? <p>No heatmap data available</p> :
                                    <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">THURSDAY</h3>
                            {timeBlocks && numberClasses && (Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['th']}
                                             day='th' buildingList={buildingFilter}
                                             numClassroomsList={numberClasses['th']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div> : timeBlocks && numberClasses ? <p>No heatmap data available</p> :
                                    <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">FRIDAY</h3>
                            {timeBlocks && numberClasses && (Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['F']}
                                             day='F' buildingList={buildingFilter}
                                             numClassroomsList={numberClasses['F']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div> : timeBlocks && numberClasses ? <p>No heatmap data available</p> :
                                    <p>Loading...</p>}
                        </div>
                    </div>
                </div>
            </div>
        </div>);
}