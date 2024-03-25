import logo from './images/carroll_logo.png';
import './Navbar.css';
import {Link} from "react-router-dom";
import {Button} from "rsuite";

export default function NavBar() {
    return (
        <nav className="navbar navbar-dark">
            <div className="container-fluid">
                <Link to={`/`}><img className="logo" src={logo} alt="Carroll College Logo"/></Link>
                <Link to={`/upload`}><Button>Upload File</Button></Link>
            </div>
        </nav>
    );
}