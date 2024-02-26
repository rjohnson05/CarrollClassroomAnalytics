import React, {useEffect, useState} from "react";
import 'primeicons/primeicons.css'
import axios from "axios";

import './Calendar.css';
import HeatMap from "./Heatmap";
import NavBar from "./NavBar";


export default function Home() {
    const [timeBlocks, setTimeBlocks] = useState({});
    const [numberClasses, setNumberClasses] = useState({});
    const [filterOpen, setFilterOpen] = useState(false);
    const [buildingFilterList, setBuildingFilterList] = useState([]);
    const [buildingNames, setBuildingNames] = useState({});

    useEffect( () => {
        console.log("List: ", buildingFilterList)
        async function fetchData() {
            await loadData();
        }
        fetchData();
    }, [buildingFilterList]);


    /**
     * Loads the data from the backend. This loads two dictionaries. The first contains the time block divisions, and the
     * second contains the number of classes running during each time block. Both of these dictionaries are stored as state.
     */
    const loadData = async () => {
        try {
            const classesData = await axios.get("http://localhost:8000/api/get_number_classes",
                {params: {buildings: buildingFilterList}});
            setTimeBlocks(classesData.data[0]);
            setNumberClasses(classesData.data[1]);

            const buildingNamesData = await axios.get("http://localhost:8000/api/get_building_names");
            setBuildingNames(buildingNamesData.data);
        } catch (error) {
            console.error(error);
        }
    }

    /**
     * Changes the current building filter based on the number of checkboxes the user has checked. This is used for
     * altering the appearance of the heatmaps. If a box is checked, the corresponding building abbrevation is added to
     * the list. If the box is unchecked, its abbreviation is removed.
     *
     * @param building  list of dictionary objects holding the abbreviation for the checked buildings
     */
    const filterBuilding = (building) => {
        setBuildingFilterList(prevList => {
            if (buildingFilterList.includes(building['abbrev'])) {
                return prevList.filter(item => item !== building['abbrev']);
            } else {
                return [...prevList, building['abbrev']]
            }
        });
    }


    return (
        <div>
            <NavBar />
            <h1 className="main-title header-font">CLASSROOM UTILIZATION OVERVIEW</h1>

            <div className="filter-container">
                <button className="filter-button" onClick={() => {setFilterOpen(!filterOpen)}}>
                <span className="pi pi-filter-fill filter-icon"></span>FILTER</button>

                {filterOpen &&
                    <form className="filter-dropdown">
                        {Object.keys(buildingNames).map(abbrev => (
                            <div>
                                <input type="checkbox" name={abbrev} onClick={() => filterBuilding({abbrev})} />
                                <label className="filter-options" htmlFor={abbrev}>{buildingNames[abbrev]}</label>
                            </div>
                        ))}
                    </form>
                }
            </div>

            <div className="days-container">
            <div className="day">
                    <h3 className="day-header">MONDAY</h3>
                    {/* Displays the heatmap for a single day once it has successfully loaded. Until then, only the
                     Loading text is displayed */}
                    {timeBlocks ?
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