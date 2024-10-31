import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import Header from "./Header.jsx"
import Footer from "./footer.jsx"
import Body from "./body.jsx"

export default function Homepage() {
    return (
        <div className="bg-gray-50 min-h-screen">
            <Header />
            <Body />
            <Footer />
        </div>
    );
}
