import React, { useState, useEffect } from "react";
import "./ee.css";

const EE = () => {
    const [position, setPosition] = useState({ top: 0, left: 0 });
    const handleMouseMove = (e: MouseEvent) => {
        setPosition({ top: e.clientY, left: e.clientX });
    };

    useEffect(() => {
        document.addEventListener("mousemove", handleMouseMove);
        return () => {
            document.removeEventListener("mousemove", handleMouseMove);
        };
    }, []);

    return (
        <div
            className="pet"
            style={{ top: `${position.top}px`, left: `${position.left}px` }}
        >
            🦜🕸
        </div>
    );
};

export default EE;
