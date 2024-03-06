import axios from "axios";
import {useEffect, useState} from "react";
import {useLocation} from "react-router-dom";

export default function UsedClassrooms() {
    const [classroomsData, setClassroomsData] = useState(null);
    const {day, buildingList, startTime, endTime} = useLocation().state;

    useEffect(() => {
        async function fetchData() {
            await loadData();
        }
        fetchData();
    }, []);

    const loadData = async () => {
        try {
            // Loads the time blocks for the week and the number of classes for each time block
            const classroomsData = await axios.get("http://localhost:8000/api/get_used_classrooms/",
                {params: {day: day, buildings: buildingList, startTime: startTime, endTime: endTime}});
            setClassroomsData(classroomsData.data);
        } catch (error) {
            console.error(error);
        }
    }

    return(
        <div>
            <h1>Classrooms in Use from {startTime} - {endTime}</h1>

            {classroomsData ?
                Object.entries(classroomsData).map(([classroom, data]) => (
                    <div key={classroom}>
                        <p>{classroom}</p>
                    </div>
                )) : <p>Loading Time Block Data</p>}
        </div>
    );
}