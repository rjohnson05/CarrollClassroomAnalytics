import axios from "axios";
import {useEffect, useState} from "react";
import {useLocation, Link} from "react-router-dom";
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import InfoIcon from '@mui/icons-material/Info';
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

    /**
     * Loads the list of classrooms used during the specified time block on a given day.
     */
    const loadData = async () => {
        try {
            const usedClassroomsData = await axios.get("http://localhost:8000/api/get_used_classrooms/",
                {params: {day: day, buildings: buildingList, startTime: startTime, endTime: endTime}});
            setClassroomsData(usedClassroomsData.data);
        } catch (error) {
            console.error(error);
        }
    }

    /**
     * Initializes the dropdown dictionary, used for the purpose of expanding the list of courses held in each classroom
     * during this time block. The dictionary designates which classrooms are currently expanded and showing its course(s).
     * Initially, none of the classrooms show their course(s).
     */
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

    /**
     * Toggles whether the given classroom is showing its course(s).
     *
     * @param classroomName  Name of the classroom being toggled
     */
    const dropdownToggle = (classroomName) => {
        setClassroomDropdownStatus(prevState => {
            const updatedStatus = {...prevState};
            updatedStatus[classroomName] = !updatedStatus[classroomName];
            return updatedStatus;
        });
    }

    /**
     * Determine whether a given classroom is currently showing its course(s).
     *
     * @param classroom  Name of the classroom in question
     */
    const isClicked = (classroom) => {
        return classroomDropdownStatus[classroom];
    }

    /**
     * Displays the list of classrooms and its corresponding courses in an orderly format, using several columns.
     */
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
                        <div className="dropdown-title">
                            {classroomDropdownStatus && isClicked(classroom) ?
                                <KeyboardArrowUpIcon className="dropdown-icon"/> :
                                <KeyboardArrowDownIcon className="dropdown-icon"/>}
                            <p className="classroom-title">{classroom}</p>
                        </div>
                        <Link className="info-icon" to={`/classrooms/${classroom}`}><InfoIcon /></Link>
                    </div>
                    {/*Displays the list of courses held within the classroom when clicked on*/}
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
                    <div className={`classroom ${classroomDropdownStatus && isClicked(classroom) ? 'classroom-square' : ''}`}
                        onClick={() => dropdownToggle(classroom)}>
                        <div className="dropdown-title">
                            {classroomDropdownStatus && isClicked(classroom) ?
                                <KeyboardArrowUpIcon className="dropdown-icon"/> :
                                <KeyboardArrowDownIcon className="dropdown-icon"/>}
                            <p className="classroom-title">{classroom}</p>
                        </div>
                        <Link className="info-icon" to={`/classrooms/${classroom}`}><InfoIcon /></Link>
                    </div>
                    <div className={`courses ${classroomDropdownStatus && isClicked(classroom) ? 'courses-visible' : ''}`}>
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