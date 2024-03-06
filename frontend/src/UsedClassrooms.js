import axios from "axios";
import {useEffect, useState} from "react";
import {useLocation} from "react-router-dom";
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import NavBar from "./analytics_home/NavBar";
import "./UsedClassrooms.css"

export default function UsedClassrooms() {
    const [classroomsData, setClassroomsData] = useState(null);
    const [classroomDropdownStatus, setClassroomDropdownStatus] = useState(null);
    const {day, buildingList, startTime, endTime} = useLocation().state;

    useEffect(() => {
        async function fetchData() {
            await loadData();
        }
        if (classroomsData == null) {
            fetchData();
        }
        setDropdownInitialStatus();
    }, [classroomsData]);

    const loadData = async () => {
        try {
            const usedClassroomsData = await axios.get("http://localhost:8000/api/get_used_classrooms/",
                {params: {day: day, buildings: buildingList, startTime: startTime, endTime: endTime}});
            setClassroomsData(usedClassroomsData.data);
        } catch (error) {
            console.error(error);
        }
    }

    const setDropdownInitialStatus = () => {
        if (!classroomsData) {
            return;
        }
        let dropdownDict = {}
        for (const key of Object.keys(classroomsData)) {
            dropdownDict[key] = false;
        }
        setClassroomDropdownStatus(dropdownDict);
    }

    const dropdownToggle = (classroomName) => {
        setClassroomDropdownStatus(prevState => {
            const updatedStatus = {...prevState};
            updatedStatus[classroomName] = !updatedStatus[classroomName];
            return updatedStatus;
        });
    }

    const isClicked = (classroom) => {
        return classroomDropdownStatus[classroom];
    }

    const renderCols = () => {
        const classrooms = classroomsData ? Object.entries(classroomsData) : [];
        const num_rows = classrooms.length / 2;

        // Shows only one column if there is only one classroom to be displayed
        if (Math.round(num_rows) === 1) {
            return (
                classrooms.map(([classroom, data]) => (
                <div className="class-group" key={classroom}>
                    <div
                        className={`classroom ${classroomDropdownStatus && isClicked(classroom) ? 'classroom-square' : ''}`}
                        onClick={() => dropdownToggle(classroom)}>
                        {classroomDropdownStatus && isClicked(classroom) ?
                            <KeyboardArrowUpIcon className="dropdown-icon"/> :
                            <KeyboardArrowDownIcon className="dropdown-icon"/>}
                        <p className="classroom-title">{classroom}</p>
                    </div>
                    <div
                        className={`courses ${classroomDropdownStatus && isClicked(classroom) ? 'courses-visible' : ''}`}>
                        {classroomDropdownStatus && classroomDropdownStatus[classroom] ?
                            data.map((course) => (
                                <div className="course" key={course}>
                                    <p className="course-title">{course[0]}</p>
                                    <p className="course-instructor"><b>Instructor: </b>{course[1]}</p>
                                    <p className="course-seats"><b>Empty Seats: </b> {course[2] - course[3]}</p>
                                </div>
                            )) : <div></div>
                        }
                    </div>
                </div>
            )))
        }

        // Displays the classrooms in several independent columns
        const cols = [];
        for (let i = 0; i < classrooms.length; i += num_rows) {
            const col = classrooms.slice(i, i + num_rows).map(([classroom, data]) => (
                <div className="class-group" key={classroom}>
                    <div
                        className={`classroom ${classroomDropdownStatus && isClicked(classroom) ? 'classroom-square' : ''}`}
                        onClick={() => dropdownToggle(classroom)}>
                        {classroomDropdownStatus && isClicked(classroom) ?
                            <KeyboardArrowUpIcon className="dropdown-icon"/> :
                            <KeyboardArrowDownIcon className="dropdown-icon"/>}
                        <p className="classroom-title">{classroom}</p>
                    </div>
                    <div
                        className={`courses ${classroomDropdownStatus && isClicked(classroom) ? 'courses-visible' : ''}`}>
                        {classroomDropdownStatus && classroomDropdownStatus[classroom] ?
                            data.map((course) => (
                                <div className="course" key={course}>
                                    <p className="course-title">{course[0]}</p>
                                    <p className="course-instructor"><b>Instructor: </b>{course[1]}</p>
                                    <p className="course-seats"><b>Empty Seats: </b> {course[2] - course[3]}</p>
                                </div>
                            )) : <div></div>
                        }
                    </div>
                </div>
            ))
            cols.push(col);
        }
        return cols;
    };

    return (
        <div>
            <NavBar/>
            <h1 className="classrooms-header">CLASSROOM USAGE REPORT <br/>({startTime} - {endTime})</h1>

            <div className="allClasses">
                {renderCols().map((col, index) => (
                    <div className="classroomsCol" key={index}>
                        {col}
                    </div>
                ))}
            </div>
        </div>
    );
}