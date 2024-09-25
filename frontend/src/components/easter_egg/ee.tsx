import React, { useState, useEffect } from "react";
import "./ee.css";

// ask the bot about LangChain or LangGraph :D
const EE = () => {
    // Store the current mouse position
    const [position, setPosition] = useState({ top: 0, left: 0 });

    // Update position on mouse move
    const handleMouseMove = (e: MouseEvent) => {
        setPosition({ top: e.clientY, left: e.clientX });
    };

    // Attach mousemove event listener on mount, detach on unmount
    useEffect(() => {
        document.addEventListener("mousemove", handleMouseMove);
        return () => {
            document.removeEventListener("mousemove", handleMouseMove);
        };
    }, []);

    // Render a div that follows the cursor with the specified emoji
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
