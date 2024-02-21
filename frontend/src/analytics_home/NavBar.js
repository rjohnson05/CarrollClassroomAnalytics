import logo from './carroll_logo.png';
import './Navbar.css';
export default function NavBar() {
    return (
        <nav className="navbar navbar-dark">
            <div className="container-fluid">
                <img className="logo" src={logo} alt="Carroll College Logo"/>
            </div>
        </nav>
    );
}