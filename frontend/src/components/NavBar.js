import logo from '../images/carroll_logo.png';
import '../css/Navbar.css';
import {Link} from "react-router-dom";
import AddIcon from '@mui/icons-material/Add';

export default function NavBar() {
    return (
        <nav className="navbar navbar-dark">
            <div className="container-fluid">
                <Link to={`/`}><img className="logo" src={logo} alt="Carroll College Logo"/></Link>
                <Link to={`/upload`}><div className="upload-button">
                    <AddIcon className="plus-icon" />
                    <p className="upload-text">Upload File</p></div>
                </Link>
            </div>
        </nav>
    );
}