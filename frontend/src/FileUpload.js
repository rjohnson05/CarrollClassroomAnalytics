import NavBar from "./analytics_home/NavBar";
import {useEffect, useState} from "react";
import axios from "axios";
import "./FileUpload.css";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import CloudUploadIcon from '@mui/icons-material/CloudUpload';


/**
 * Displays the page for file uploading. This page allows the user to upload an Excel spreadsheet for either classroom data
 * or course schedule data. The data from the uploaded spreadsheet is used to populate the database.
 *
 * @author Ryan Johnson
 */
export default function FileUpload() {
    const [fileErrorShowing, setFileErrorShowing] = useState(false);
    const [successText, setSuccessText] = useState(false);
    const [uploadingText, setUploadingText] = useState(false);
    const [scheduleFile, setScheduleFile] = useState();
    const [classroomFile, setClassroomFile] = useState();
    const [uploadOptionDropdownStatus, setUploadOptionDropdownStatus] = useState({
        "schedule": false,
        "classroom": false,
    });

    useEffect(() => {
    }, [scheduleFile, classroomFile]);

    /**
     * Changes the file being uploaded whenever the file browser is used.
     * @param e Event determining which file was chosen
     */
    const handleFileChange = (e) => {
        if (e.target.id === "classroom-chooser") {
            setClassroomFile(e.target.files[0]);
        } else {
            setScheduleFile(e.target.files[0]);
        }
    }

    /**
     * Sends the uploaded file to the Django endpoint /upload_file/, where the ORM is used to create objects with the data
     * and populate the database.
     *
     * @param e Event indicating that the form has been submitted
     */
    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('dataType', e.target.id);

        if (e.target.id === "classroom") {
            formData.append('file', classroomFile);
            formData.append("fileName", classroomFile.name);
        } else {
            formData.append('file', scheduleFile);
            formData.append("fileName", scheduleFile.name);
        }

        // Only show the uploading text while the file is uploading to the database
        setUploadingText(true);
        setSuccessText(false);
        setFileErrorShowing(false);

        const uploadSuccess = axios.post("http://localhost:8000/api/upload_file/", formData, {
            headers: {
                'content-type': 'multipart/form-data',
            }
        }).then(r => {
                // Shows the success text upon a successful file upload
                setUploadingText(false);
                setSuccessText(true);
                setFileErrorShowing(false);
                console.log(r.data)})
            .catch(error => {
                // Shows the error message if the file has invalid column names
                setUploadingText(false);
                setSuccessText(false);
                setFileErrorShowing(true)});

        // After uploading the files, reset them to empty
        if (e.target.id === "classroom") {
            setClassroomFile(null);
        } else {
            setScheduleFile(null);
        }
    }

    /**
     * Toggles whether the given data type displays its form for uploading a spreadsheet.
     *
     * @param dataType  Type of spreadsheet being uploaded: accepts either schedule or classroom data
     */
    const dropdownToggle = (dataType) => {
        setUploadOptionDropdownStatus(prevState => {
            const updatedStatus = {...prevState};
            updatedStatus[dataType] = !updatedStatus[dataType];
            return updatedStatus;
        });
    }

    /**
     * Determine whether a given classroom is currently showing its course(s).
     *
     * @param uploadOption  Name of the classroom in question
     */
    const isClicked = (uploadOption) => {
        return uploadOptionDropdownStatus[uploadOption];
    }


    return (
        <div>
            <NavBar />
            <h1 className="title-font">UPLOAD DATA</h1>
            {uploadingText &&
                <p className="info-text">Uploading...</p>}
            {successText &&
                <p className="info-text">File successfully uploaded.</p>}
            {fileErrorShowing &&
                <p className="info-text">This file has improper formatting. Fix this and then try uploading again.</p>}

            {/*Creates the dropdown for uploading schedule data*/}
            <div className={`upload-option ${uploadOptionDropdownStatus && isClicked("schedule") ? 'upload-option-square' : ''}`}>
                {/*Creates the main block that houses the dropdown*/}
                <div className="upload-option-dropdown" onClick={() => dropdownToggle("schedule")}>
                    {uploadOptionDropdownStatus && isClicked("schedule") ?
                            <KeyboardArrowUpIcon className="dropdown-icon"/> :
                            <KeyboardArrowDownIcon className="dropdown-icon"/>}
                    <p className="option-title">Upload Schedule Data</p>
                </div>
                <div className={`dropdown ${uploadOptionDropdownStatus && isClicked("schedule") ? 'dropdown-visible' : ''}`}>
                    {uploadOptionDropdownStatus && uploadOptionDropdownStatus["schedule"] ?
                        <div>
                            <form className="upload-area"  id="schedule" onSubmit={handleSubmit} method="POST">
                                <div className="file-chooser-block">
                                    <input id="schedule-chooser" type="file" accept=".xls, .xlsx" onChange={handleFileChange} hidden />
                                    <label htmlFor="schedule-chooser" className="file-chooser">
                                        <CloudUploadIcon />
                                        <p className="upload-label">Choose Schedule Spreadsheet</p>
                                    </label>
                                    {scheduleFile ? <p className="file-name-preview"><b>File Name: </b>{scheduleFile.name}</p> : <p></p>}
                                </div>

                                <button className="submit-button" type="submit">Upload File</button>
                            </form>
                        </div>
                        : <div></div>
                    }
                </div>
            </div>

            {/*Creates the dropdown for uploading classroom data*/}
            <div
                className={`upload-option ${uploadOptionDropdownStatus && isClicked("classroom") ? 'upload-option-square' : ''}`}>
                <div className="upload-option-dropdown" onClick={() => dropdownToggle("classroom")}>
                    {uploadOptionDropdownStatus && isClicked("classroom") ?
                        <KeyboardArrowUpIcon className="dropdown-icon"/> :
                        <KeyboardArrowDownIcon className="dropdown-icon"/>}
                    <p className="option-title">Upload Classroom Data</p>
                </div>
                <div
                    className={`dropdown ${uploadOptionDropdownStatus && isClicked("classroom") ? 'dropdown-visible' : ''}`}>
                    {uploadOptionDropdownStatus && uploadOptionDropdownStatus["classroom"] ?
                        <div>
                            <form className="upload-area"  id="classroom" onSubmit={handleSubmit} method="POST">
                                <div className="file-chooser-block">
                                    <input id="classroom-chooser" type="file" accept=".xls, .xlsx" onChange={handleFileChange} hidden/>
                                    <label htmlFor="classroom-chooser" className="file-chooser">
                                        <CloudUploadIcon/>
                                        <p className="upload-label">Choose Classroom Spreadsheet</p>
                                    </label>
                                    {classroomFile ? <p className="file-name-preview"><b>File Name: </b>{classroomFile.name}</p> :
                                        <p></p>}
                                </div>

                                <button className="submit-button" type="submit">Upload File</button>
                            </form>
                        </div>
                        : <div></div>
                    }
                </div>
            </div>
        </div>
    );
}