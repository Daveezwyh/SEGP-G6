import { PiBroomBold } from "react-icons/pi";

export default function Header() {
  return (
    <nav className="navbar navbar-expand-md navbar-light bg-white shadow-lg">
      <div className="container-fluid">
       <a className="navbar-brand mb-0 ml-[3%] h1 navbar " ><PiBroomBold size="45"/>AutoClean </a>
        <button className="navbar-toggler collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
           <span className="navbar-toggler-icon"></span>
        </button>
        {/*Placceholder-  bug: after collapse text is not shown */}
        <div className="navbar-collapse" id="navbarSupportedContent">
          <div className="navbar-nav">
            <a className="nav-link active" href="#">Home </a>
            <a className="nav-link" href="#">Features</a>
            <a className="nav-link" href="#">Pricing</a>
            <a className="nav-link disabled" href="#">Disabled</a>
          </div>   
        </div>  
      </div>
    </nav>
  );
}


