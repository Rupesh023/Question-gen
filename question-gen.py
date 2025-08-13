"""
Math Question Generator using Google Gemini Flash API
"""

import json
import os
from typing import List, Dict
from dataclasses import dataclass
import google.generativeai as genai  # pip install google-generativeai


@dataclass
class Question:
    title: str
    description: str
    question_text: str
    instruction: str
    difficulty: str
    order: int
    options: List[str]
    correct_answer_index: int
    explanation: str
    subject: str
    unit: str
    topic: str
    plusmarks: int = 1


class MathQuestionGenerator:
    def __init__(self, api_key: str):
        """
        Initialize the generator with Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

        self.base_questions = [
            {
                "text": """Each student at Central Middle School wears a uniform consisting of 1 shirt and 1 pair of pants. 
                The table shows the colors available for each item of clothing. How many different uniforms are possible?
                
                Shirt Colors: Tan, Red, White, Yellow
                Pants Colors: Black, Khaki, Navy
                
                (A) Three (B) Four (C) Seven (D) Ten (E) Twelve""",
                "type": "combinatorics",
                "subject": "Quantitative Math",
                "unit": "Data Analysis & Probability",
                "topic": "Counting & Arrangement Problems"
            },
            {
                "text": """The top view of a rectangular package of 6 tightly packed balls is shown. 
                If each ball has a radius of 2 centimeters, which of the following are closest to the dimensions, 
                in centimeters, of the rectangular package?
                
                (A) 2×3×6 (B) 4×6×6 (C) 2×4×6 (D) 4×8×12 (E) 6×8×12""",
                "type": "geometry_measurement",
                "subject": "Quantitative Math",
                "unit": "Geometry and Measurement",
                "topic": "Solid Figures (Volume of Cubes)"
            }
        ]

    def generate_question_prompt(self, base_question: Dict, question_number: int) -> str:
        return f"""
Create a math question similar to the following base question, but with different context and numbers:

BASE QUESTION: {base_question['text']}
TYPE: {base_question['type']}
CURRICULUM: {base_question['subject']} -> {base_question['unit']} -> {base_question['topic']}

Requirements:
1. Create a completely NEW scenario (different context, objects, numbers)
2. Maintain the same mathematical concept and difficulty level
3. Provide 5 multiple choice options (A-E)
4. Make sure there's only ONE correct answer
5. Include clear step-by-step solution reasoning

Format your response as JSON:
{{
    "question_text": "Your question here",
    "instruction": "Clear instruction for students",
    "options": ["Option A", "Option B", "Option C", "Option D", "Option E"],
    "correct_answer_index": 2,
    "explanation": "Step-by-step explanation of the solution",
    "difficulty": "easy/moderate/hard"
}}
"""

    def call_gemini_api(self, prompt: str) -> Dict:
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            json_str = content[start_idx:end_idx]
            return json.loads(json_str)
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return self.generate_fallback_question()

    def generate_fallback_question(self) -> Dict:
        return {
            "question_text": "A school cafeteria offers 3 types of sandwiches, 4 types of drinks, and 2 types of chips. How many different lunch combinations are possible?",
            "instruction": "Calculate the total number of possible lunch combinations.",
            "options": ["9", "24", "14", "12", "18"],
            "correct_answer_index": 1,
            "explanation": "Using the multiplication principle: 3 × 4 × 2 = 24 combinations",
            "difficulty": "moderate"
        }

    def create_question_object(self, ai_response: Dict, base_question: Dict, question_num: int) -> Question:
        return Question(
            title=f"Math Assessment Question {question_num}",
            description="Auto-generated math assessment question",
            question_text=ai_response["question_text"],
            instruction=ai_response["instruction"],
            difficulty=ai_response["difficulty"],
            order=question_num,
            options=ai_response["options"],
            correct_answer_index=ai_response["correct_answer_index"],
            explanation=ai_response["explanation"],
            subject=base_question["subject"],
            unit=base_question["unit"],
            topic=base_question["topic"]
        )

    def format_question_output(self, question: Question) -> str:
        output = (
            f"@title {question.title}\n\n"
            f"@description {question.description}\n\n"
            f"@question {question.question_text}\n\n"
            f"@instruction {question.instruction}\n\n"
            f"@difficulty {question.difficulty}\n\n"
            f"@order {question.order}\n\n"
        )
        for i, option in enumerate(question.options):
            marker = "@@option" if i == question.correct_answer_index else "@option"
            output += f"{marker} {option}\n\n"

        output += (
            "@explanation\n"
            f"{question.explanation}\n\n"
            f"@subject {question.subject}\n\n"
            f"@unit {question.unit}\n\n"
            f"@topic {question.topic}\n\n"
            f"@plusmarks {question.plusmarks}\n\n"
            "---\n\n"
        )
        return output

    def generate_questions(self, num_questions: int = 2) -> str:
        all_questions = ""
        for i in range(num_questions):
            base_question = self.base_questions[i % len(self.base_questions)]
            print(f"Generating question {i + 1} based on {base_question['type']}...")
            prompt = self.generate_question_prompt(base_question, i + 1)
            ai_response = self.call_gemini_api(prompt)
            question = self.create_question_object(ai_response, base_question, i + 1)
            all_questions += self.format_question_output(question)
        return all_questions

    def save_to_file(self, content: str, filename: str = "generated_questions.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Questions saved to {filename}")


def main():
    API_KEY = os.getenv("GEMINI_API_KEY") 
    genai.configure(api_key=API_KEY)  
    generator = MathQuestionGenerator(API_KEY)
    print("Starting question generation...")
    questions = generator.generate_questions(num_questions=2)
    generator.save_to_file(questions)
    print("\n" + "=" * 50)
    print("GENERATED QUESTIONS:")
    print("=" * 50)
    print(questions)


if __name__ == "__main__":
    main()
