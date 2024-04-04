import React from 'react';
import ReactDOM from 'react-dom/client';
import {createBrowserRouter, RouterProvider} from "react-router-dom";
import './index.css';
import Calendar from './components/HeatmapSchedule';
import UsedClassrooms from "./components/UsedClassrooms";
import reportWebVitals from './reportWebVitals';
import ClassroomInfo from "./components/ClassroomInfo";
import FileUpload from "./components/FileUpload";

/**
 * Contains the router for the Carroll Classroom Analytics software, directing to the correct components based upon the URL.
 *
 * @author Ryan Johnson
 */
const router = createBrowserRouter([{
    path: "/", element: <Calendar/>
}, {
    path: "/used_classrooms/", element: <UsedClassrooms/>
}, {
    path: "/classrooms/:id", element: <ClassroomInfo/>
}, {
    path: "/upload", element: <FileUpload/>
}])

// Serves as the launch point for the frontend of the application
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<React.StrictMode>
    <RouterProvider router={router}/>
</React.StrictMode>);
