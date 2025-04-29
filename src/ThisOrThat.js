import React, { useState } from "react";
import "./ThisOrThat.css";

const questions = [
  {
    question: "If you could live anywhere in the world, would you choose a bustling city or a quiet countryside?",
    option1: "Bustling City",
    option2: "Quiet Countryside",
  },
  {
    question: "Would you rather have unlimited travel opportunities but no home or a beautiful home but no travel?",
    option1: "Unlimited Travel",
    option2: "Beautiful Home",
  },
  {
    question: "If you could master any skill instantly, would it be playing a musical instrument or speaking a new language?",
    option1: "Musical Instrument",
    option2: "New Language",
  },
  {
    question: "Do you prefer being surrounded by a group of friends or having time to yourself?",
    option1: "Group of Friends",
    option2: "Time to Yourself",
  },
  {
    question: "Would you rather explore the mysteries of space or the hidden wonders of the ocean?",
    option1: "Mysteries of Space",
    option2: "Hidden Wonders of the Ocean",
  },
];

function ThisOrThat() {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [animationClass, setAnimationClass] = useState("fade-in");

  const handleOptionClick = (option) => {
    setAnimationClass("fade-out"); // Trigger fade-out animation
    setTimeout(() => {
      const newSelectedOptions = [...selectedOptions, option];
      setSelectedOptions(newSelectedOptions);

      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
      } else {
        alert("You have completed all questions!");
        console.log("Selected options:", newSelectedOptions);
      }

      setAnimationClass("fade-in"); // Reset to fade-in for the next question
    }, 500); // Match the animation duration
  };

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="app">
      <div className={`question-container ${animationClass}`}>
        <p className="question-text">{currentQuestion.question}</p>
        <div className="options">
          <div
            className="option-card option-left"
            onClick={() => handleOptionClick(currentQuestion.option1)}
          >
            {currentQuestion.option1}
          </div>
          <div
            className="option-card option-right"
            onClick={() => handleOptionClick(currentQuestion.option2)}
          >
            {currentQuestion.option2}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ThisOrThat;
