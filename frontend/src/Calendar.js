import React, {useEffect, useState} from "react";
import axios from "axios";

export default function Home() {
    const [data, setData] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        // Loads the data from the backend upon the page's initial loading
        try {
            const response = await axios.get("http://localhost:8000/")
            setData(response.data)
        } catch (error) {
            console.error(error)
        }
    };

    return (
        <div>
            <p>Output:{data && data.message}</p>
        </div>
    )
}