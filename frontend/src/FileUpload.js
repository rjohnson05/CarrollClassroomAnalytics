import NavBar from "./analytics_home/NavBar";
import {useEffect, useState} from "react";
import axios from "axios";
import "./FileUpload.css";

export default function FileUpload() {
    const [dataType, setDataType] = useState();
    const [file, setFile] = useState();

    useEffect(() => {
        console.log("File", file);
    }, [file]);

    const handleRadioChange = (e) => {
        setDataType(e.target.id);
    }

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    }

    const handleSubmit = (e) => {
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

            <form onSubmit={handleSubmit}>
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