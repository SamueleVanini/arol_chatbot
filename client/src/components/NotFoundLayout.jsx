import {Link} from "react-router-dom";
import notfoundLottie from "../assets/notfound-404.json";
import Lottie from "lottie-react";

export function NotFoundLayout() {
    return(
        <div className="d-flex flex-column justify-content-center align-items-center">
            <h2>Ooop!... page not found!</h2>
            <Lottie animationData={notfoundLottie} className="w-30 align-self-center"/>
            <Link to="/" className="btn btn-primary mt-2 w-50 align-self-center">Go Home!</Link>
        </div>
    );
}