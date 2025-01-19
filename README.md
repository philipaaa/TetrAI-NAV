TetrAI Nav

TetrAI Nav is an innovative project developed for the NAV Canada Hackathon Challenge. Combining the logic of Tetris with artificial intelligence (AI) and aviation navigation principles, TetrAI Nav offers an engaging and efficient approach to optimizing air traffic management.

Table of Contents

Overview

Features

How It Works

Installation

Usage

Technologies Used

Team

Overview

TetrAI Nav leverages AI to analyze complex aviation navigation challenges and provides human operators with actionable suggestions. Our solution integrates a hybrid decision-making model:

AI Determines: AI processes data and identifies optimal navigation solutions.

AI Suggests: AI presents its suggestions in an understandable and actionable format.

Human Decides: The final decision rests with human operators to ensure accountability and safety.

This project showcases how AI can complement human expertise, fostering trust and collaboration in critical operations like air traffic control.

Features

Hybrid Decision Model: Blends AI's computational power with human judgment.

Real-Time Navigation Suggestions: AI processes data to suggest optimal flight paths.

Accountability Visualization: Highlights the roles of AI and human operators in decision-making.

User-Friendly Interface: Intuitive UI with a Tetris-inspired design for visualizing navigation challenges.

How It Works

Data Input: The system receives data on flight paths, weather, and air traffic conditions.

AI Processing: Using advanced algorithms, the AI analyzes the data to determine optimal solutions.

Recommendations: AI presents its suggestions through the user interface.

Human Oversight: Operators evaluate and select the appropriate decision based on AI’s recommendations.

Installation

To run TetrAI Nav locally, follow these steps:

Clone the Repository:

git clone https://github.com/philipaaa/tetrAI-nav.git
cd tetrAI-nav

Install Dependencies:

pip install -r requirements.txt

Run the Application:

python main.py

Usage

Start the application by running the main.py file.

Use the side panel to:

Enable or disable AI-controlled suggestions.

Start or pause the decision-making process.

Observe navigation solutions provided by the AI and make decisions as an operator.

Technologies Used

Programming Language: Python (with PyQt for GUI)

Libraries:

NumPy

PyQt5

Custom AI algorithms for navigation optimization

Design: Tetris-inspired UI with aviation-themed elements

Team

This project was developed by Luigi Zagaria, Philip Papadadatos, Antoine Khayat and Terrence Manley-Elliot combining expertise in AI, software development, and aviation navigation.

Acknowledgments

NAV Canada Hackathon: For providing the platform and challenge.

Tetris: For inspiring the visualization and problem-solving mechanics.

License

This project is licensed under the MIT License.
