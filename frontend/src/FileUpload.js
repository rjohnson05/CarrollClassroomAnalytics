import NavBar from "./analytics_home/NavBar";
import {useEffect, useState} from "react";
import axios from "axios";
import "./FileUpload.css";


/**
 * Displays the page for file uploading. This page allows the user to upload an Excel spreadsheet for either classroom data
 * or course schedule data. The data from the uploaded spreadsheet is used to populate the database.
 *
 * @author Ryan Johnson
 */
export default function FileUpload() {
    const [dataType, setDataType] = useState();
    const [file, setFile] = useState();

    useEffect(() => {
        console.log("File", file);
    }, [file]);

    /**
     * Changes the type of spreadsheet data being uploaded whenever the radio buttons are changed.
     * @param e Event determining which radio button was clicked
     */
    const handleRadioChange = (e) => {
        setDataType(e.target.id);
    }

    /**
     * Changes the file being uploaded whenever the file browser is used.
     * @param e Event determining which file was chosen
     */
    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    }

    /**
     * Sends the uploaded file to the Django endpoint /upload_file/, where the ORM is used to create objects with the data
     * and populate the database.
     *
     * @param e Event indicating that the form has been submitted
     */
    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("Handling submit");
        const formData = new FormData();
        formData.append('dataType', dataType);
        formData.append('file', file);
        formData.append("fileName", file.name);

        axios.post("http://localhost:8000/api/upload_file/", formData, {
            headers: {
                'content-type': 'multipart/form-data',
            }
        }).then(r => console.log(r.data));
    }


    return (
        <div>
            <NavBar />
            <h1 className="title-font">UPLOAD DATA</h1>

            <form onSubmit={handleSubmit} method="POST">
                <input type="radio" id="classroom" name="data_type" onChange={handleRadioChange}/>
                <label form="classroom">Upload Classroom Data</label><br/>
                <input type="radio" id="schedule" name="data_type" onChange={handleRadioChange}/>
                <label form="schedule">Upload Schedule Data</label><br/>
                <input type="file" onChange={handleFileChange}/><br/>
                <button type="submit">Upload File</button>
            </form>
        </div>
    );
}