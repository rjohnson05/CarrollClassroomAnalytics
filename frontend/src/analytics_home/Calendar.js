import React, { useEffect, useState } from "react";
import 'primeicons/primeicons.css'
import axios from "axios";
import './Calendar.css';
import HeatMap from "./Heatmap";
import NavBar from "./NavBar";
import Legend from "./Legend"
import * as d3 from "d3";
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
// import { Classroom } from 'api/models.py';

export default function Home() {
    const [classrooms, setClassrooms] = useState([]);
    const [courses, setCourses] = useState([]);
    const [firstRender, setFirstRender] = useState(true);
    const [timeBlocks, setTimeBlocks] = useState(false);
    const [numberClasses, setNumberClasses] = useState(false);
    const [maxNumClasses, setMaxNumClasses] = useState(null);
    const [filterOpen, setFilterOpen] = useState(false);
    const [buildingFilter, setBuildingFilter] = useState({});
    const [buildingNames, setBuildingNames] = useState({});
    const [showTable, setShowTable] = useState(false); // State variable to toggle display

    const columns = [
        { field: 'name', header: 'Name' },
        { field: 'room_num', header: 'Room Number' },
        // { field: 'start_time', header: 'Start Time'},
        // { field: 'building', header: 'Building' },
        // { field: 'numberOfClasses', header: 'Number of Classes' }
    ];

    const columns2 = [
        // { field: 'name', header: 'Name' },
        // { field: 'room_num', header: 'Room Number' },
        { field: 'day', header: 'Day'},
        { field: 'start_time', header: 'Start Time'},
        { field: 'end_time', header: 'End Time'},
        { field: 'number_students', header: 'Number of Students'},


        // { field: 'building', header: 'Building' },
        // { field: 'numberOfClasses', header: 'Number of Classes' }
    ];


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


    // useEffect(() => {
    //     // Define a function to fetch data from your Django backend
    //     const fetchData = async () => {
    //         try {
    //             const response = await axios.get('/api/get_classroom_data/'); // Change the URL to match your Django endpoint
    //             setClassrooms(response.data); // Set the fetched data to the state
    //             console.log(response.data)
    //         } catch (error) {
    //             console.error('Error fetching data:', error);
    //         }
    //     };
    //
    //     // Call the fetchData function when the component mounts
    //     fetchData();
    // }, []);

    useEffect(() => {
    const fetchData = async () => {
        try {
            // Fetch classroom data
            const response = await axios.get('/api/get_classroom_data/');
            const classroomsData = response.data;

            // Fetch number of classes data
            // const classesData = await axios.get("http://localhost:8000/api/get_number_classes", {
            //     params: { buildings: Object.keys(buildingFilter) }
            // });
            // const numberClassesData = classesData.data[1];

            // Fetch time data
            const courseDataResponse = await axios.get("/api/get_course_data/");
            const courseData = courseDataResponse.data;

            // Map number of classes to the classrooms data
            const updatedClassrooms = classroomsData.map(classroom => {
                // const identifier = classroom.room_num;
                // const numberOfClasses = numberClassesData[identifier] || 0;
                return { ...classroom};
            });

            // Update Classrooms
            const updatedCourses = courseData.map(course => {
                // const course_identifier = courses.start_time;
                // const time = courseData[course_identifier];
                return { ... course};
            });
            //

            // Set the updated classrooms data to the state
            setClassrooms(updatedClassrooms);

            // Set the updated courses data to the state
            setCourses(updatedCourses);

            // Calculate maxNumClasses
            // let maxNumberClasses = 0;
            // Object.values(numberClassesData).forEach(numClasses => {
            //     if (numClasses > maxNumberClasses) {
            //         maxNumberClasses = numClasses;
            //     }
            // });
            // setMaxNumClasses(maxNumberClasses);
        } catch (error) {
            console.error('Error fetching data:', error);
        }

    };

    fetchData();
}, []);


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


    const toggleTableDisplay = () => {
    setShowTable(!showTable); // Toggle the state variable
    };

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

        <button onClick={toggleTableDisplay}>Toggle Table</button>

        {/* Display either the heatmap or the table based on the showTable state */}
        {showTable ? (
            <div className="card">
                <div className="table-container">
                    <table className="table" style={{minWidth: '50rem'}}>
                        <thead>
                        <tr>
                            {/* Render table headers for classroom data */}
                            {columns.map((col, i) => (
                                <th key={i}>{col.header}</th>
                            ))}
                            {/* Render table headers for course data */}
                            {columns2.map((col, i) => (
                                <th key={i + columns.length}>{col.header}</th>
                            ))}
                        </tr>
                        </thead>
                        <tbody>
                        {/* Render rows for classroom and course data */}
                        {classrooms.map((classroom, i) => (
                            <tr key={i}>
                                {/* Render cells for classroom data */}
                                {columns.map((col, j) => (
                                    <td key={j}>{classroom[col.field]}</td>
                                ))}
                                {/* Render cells for course data */}
                                {courses[i] ? ( // Check if course data exists for this index
                                    columns2.map((col2, k) => (
                                        <td key={k + columns.length}>{courses[i][col2.field]}</td>
                                    ))
                                ) : ( // Render empty cells if no course data for this index
                                    columns2.map((col2, k) => (
                                        <td key={k + columns.length}></td>
                                    ))
                                )}
                            </tr>
                        ))}
                        </tbody>
                    </table>

                </div>
            </div>
        ) : (


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
                                             day='M' buildingList={buildingFilter}
                                             numClassroomsList={numberClasses['M']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div>
                                : <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">TUESDAY</h3>
                            {(Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['T']}
                                             day='T' buildingList={buildingFilter}
                                             numClassroomsList={numberClasses['T']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div>
                                : <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">WEDNESDAY</h3>
                            {(Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['W']}
                                             day='W' buildingList={buildingFilter}
                                             numClassroomsList={numberClasses['W']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div>
                                : <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">THURSDAY</h3>
                            {(Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    <HeatMap timeBlockList={timeBlocks['th']}
                                             day='th' buildingList={buildingFilter}
                                             numClassroomsList={numberClasses['th']}
                                             maxNumberClasses={maxNumClasses}/>
                                </div>
                                : <p>Loading...</p>}
                        </div>
                        <div className="day">
                            <h3 className="day-header">FRIDAY</h3>
                            {(Object.keys(timeBlocks).length > 0 && Object.keys(numberClasses).length > 0 && maxNumClasses) ?
                                <div className="heatmap">
                                    < HeatMap timeBlockList={timeBlocks['F']}
                                              day='F' buildingList={buildingFilter}
                                              numClassroomsList={numberClasses['F']}
                                              maxNumberClasses={maxNumClasses}/>
                                </div>
                                : <p>Loading...</p>}
                        </div>
                    </div>
                </div>
            </div>
        )}
    </div>
)
};
