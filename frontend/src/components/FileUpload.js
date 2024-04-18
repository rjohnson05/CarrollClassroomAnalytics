import NavBar from "./NavBar";
import {useEffect, useState} from "react";
import axios from "axios";
import "../css/FileUpload.css";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import CloudUploadIcon from '@mui/icons-material/CloudUpload';


/**
 * Displays the page for uploading Excel spreadsheets (either for course schedule or classroom data). The data from the
 * uploaded spreadsheet replaces any data currently in the database.
 *
 * @author Ryan Johnson
 */
export default function FileUpload() {
    const [missingColumns, setMissingColumns] = useState("");
    const [fileErrorShowing, setFileErrorShowing] = useState(false);
    const [successText, setSuccessText] = useState(false);
    const [uploadingText, setUploadingText] = useState(false);
    const [scheduleFile, setScheduleFile] = useState();
    const [classroomFile, setClassroomFile] = useState();
    const [uploadOptionDropdownStatus, setUploadOptionDropdownStatus] = useState({
        "schedule": false, "classroom": false,
    });

    useEffect(() => {
    }, [scheduleFile, classroomFile]);

    /**
     * Changes the file being uploaded whenever a file is selected using one of the file browsers. This file information
     * will be sent to the database if the user submits before choosing another file.
     *
     * @param e Event holding data on which file was chosen
     */
    const handleFileChange = (e) => {
        if (e.target.id === "classroom-chooser") {
            setClassroomFile(e.target.files[0]);
        } else {
            setScheduleFile(e.target.files[0]);
        }
    }

    /**
     * Sends the uploaded file to the Django endpoint '/upload_file/', where the ORM is used to create objects with the
     * file data and populate the database. Depending on the success of loading the data into the database, a
     * success/error message is shown on the screen before the file is reset, ready for another upload. Should the upload
     * result in an error, the missing columns resulting in the error are displayed.
     *
     * @param e Event indicating that the form has been submitted
     */
    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('dataType', e.target.id);

        if (e.target.id === "classroom") {
            // Sends the uploaded classroom data file
            formData.append('file', classroomFile);
            // Hitting the upload button with no file attached shows no difference on page
            if (classroomFile === undefined) {
                return;
            }
            formData.append("fileName", classroomFile.name);
        } else {
            // Sends the uploaded course schedule file
            formData.append('file', scheduleFile);
            // Hitting the upload button with no file attached shows no difference on page
            if (scheduleFile === undefined) {
                return;
            }
            formData.append("fileName", scheduleFile.name);
        }

        // Only show the uploading text while the file is uploading to the database
        setUploadingText(true);
        setSuccessText(false);
        setFileErrorShowing(false);

        // Displays a success/error message, depending on the success of loading the data into the database.
        axios.post("/api/upload_file/", formData, {
            headers: {
                'content-type': 'multipart/form-data',
            }
        }).then(res => {
            if (!res.data['success']) {
                // Shows the error message if the file has invalid column names or isn't a .xlsx file
                setUploadingText(false);
                setSuccessText(false);
                setFileErrorShowing(true);
                setMissingColumns(res.data['missingColumns'].join(', '));
            }
            else {
                // Shows the success text upon a successful file upload
                setUploadingText(false);
                setSuccessText(true);
                setFileErrorShowing(false);
                setMissingColumns("");
            }
        });

        // After uploading the files, reset them to empty
        if (e.target.id === "classroom") {
            setClassroomFile(null);
        } else {
            setScheduleFile(null);
        }
    }

    /**
     * Toggles whether the given data type div block displays its form for uploading a spreadsheet. The data type div
     * blocks include the classroom block and the course schedule block. If either of these blocks is set to true, the
     * corresponding upload form is visible to the user.
     *
     * @param dataType  Type of spreadsheet being uploaded: accepts either course schedule or classroom data
     */
    const dropdownToggle = (dataType) => {
        setUploadOptionDropdownStatus(prevState => {
            const updatedStatus = {...prevState};
            updatedStatus[dataType] = !updatedStatus[dataType];
            return updatedStatus;
        });
    }

    /**
     * Determines whether a given upload block is currently showing its form.
     *
     * @param uploadOption  Type of spreadsheet being uploaded: accepts either course schedule or classroom data
     */
    const isClicked = (uploadOption) => {
        return uploadOptionDropdownStatus[uploadOption];
    }


    return (<div>
            <NavBar/>
            <h1 className="title-font">UPLOAD DATA</h1>
            {uploadingText && <p className="info-text">Uploading...</p>}
            {successText && <p className="info-text">File successfully uploaded.</p>}
            {fileErrorShowing &&
                <div>
                    <p className="info-text">This file has improper formatting. Add the following columns and then try
                        again:</p> <br/>
                    <p className="info-text">{missingColumns}</p>
                </div>
            }

        {/*Creates the dropdown for uploading schedule data*/}
        <div
            className={`upload-option ${uploadOptionDropdownStatus && isClicked("schedule") ? 'upload-option-square' : ''}`}>
                {/*Creates the main block that houses the dropdown*/}
                <div className="upload-option-dropdown" onClick={() => dropdownToggle("schedule")}>
                    {uploadOptionDropdownStatus && isClicked("schedule") ?
                        <KeyboardArrowUpIcon className="dropdown-icon"/> :
                        <KeyboardArrowDownIcon className="dropdown-icon"/>}
                    <p className="option-title">Upload Schedule Data</p>
                </div>
                <div
                    className={`dropdown ${uploadOptionDropdownStatus && isClicked("schedule") ? 'dropdown-visible' : ''}`}>
                    {uploadOptionDropdownStatus && uploadOptionDropdownStatus["schedule"] ? <div>
                        <form className="upload-area" id="schedule" onSubmit={handleSubmit} method="POST">
                            <div className="file-chooser-block">
                                <input id="schedule-chooser" type="file" accept=".xls, .xlsx"
                                       onChange={handleFileChange} hidden/>
                                <label htmlFor="schedule-chooser" className="file-chooser">
                                    <CloudUploadIcon/>
                                    <p className="upload-label">Choose Schedule Spreadsheet</p>
                                </label>
                                {scheduleFile ?
                                    <p className="file-name-preview"><b>File Name: </b>{scheduleFile.name}</p> :
                                    <p></p>}
                            </div>

                            <button className="submit-button" type="submit">Upload File</button>
                        </form>
                    </div> : <div></div>}
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
                    {uploadOptionDropdownStatus && uploadOptionDropdownStatus["classroom"] ? <div>
                        <form className="upload-area" id="classroom" onSubmit={handleSubmit} method="POST">
                            <div className="file-chooser-block">
                                <input id="classroom-chooser" type="file" accept=".xls, .xlsx"
                                       onChange={handleFileChange} hidden/>
                                <label htmlFor="classroom-chooser" className="file-chooser">
                                    <CloudUploadIcon/>
                                    <p className="upload-label">Choose Classroom Spreadsheet</p>
                                </label>
                                {classroomFile ?
                                    <p className="file-name-preview"><b>File Name: </b>{classroomFile.name}</p> :
                                    <p></p>}
                            </div>

                            <button className="submit-button" type="submit">Upload File</button>
                        </form>
                    </div> : <div></div>}
                </div>
            </div>
        </div>);
}