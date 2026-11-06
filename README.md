# 💰 DuitSmart – AI-Powered Financial Literacy Chatbot

**Making Financial Literacy Fun, Simple, and Accessible for Teenagers!**

DuitSmart is an AI-powered financial literacy web application designed to help Malaysian teenagers develop smart money management habits. It combines an interactive AI chatbot, gamified learning activities, savings tracking, and financial education tools to make learning about personal finance engaging and accessible.

The platform encourages teenagers to understand essential financial concepts such as budgeting, saving, smart spending, banking, investing, and scam awareness through interactive experiences.

## ✨ Key Features

### 🤖 1. AI Financial Assistant
- Interactive AI-powered chatbot for financial guidance.
- Provides personalized explanations about financial literacy.
- Supports short and detailed answer formats.
- Uses relatable Malaysian financial examples and conversational language.
- Powered by OpenAI API.

### 🎯 2. Savings Goal Tracker
- Create and manage personal savings goals.
- Set target amounts and deadlines.
- Track savings progress.
- Add contributions to existing goals.
- Monitor completed and ongoing savings goals.

### 🎮 3. Gamified Financial Learning

Includes six interactive financial education games:

| Game | Description |
|---|---|
| 🦸 Budget Hero | Learn budgeting and money management. |
| 🧮 Compound Interest Calculator | Understand how savings grow through compound interest. |
| 🧠 Money Quiz | Test financial literacy knowledge. |
| 🎡 Spin & Save | Learn saving concepts through interactive challenges. |
| 🎯 Needs vs Wants | Understand the difference between essential and non-essential spending. |
| 🏎️ Savings Race | Develop saving habits through interactive gameplay. |

### 🏆 4. Achievements & Rewards
- Earn coins and points through activities.
- Unlock achievements by completing financial challenges.
- Track game scores and achievements.
- Encourage continuous learning through gamification.

### 🥇 5. Leaderboard
- Track player performance.
- Compare scores with other players.
- Encourage friendly competition and engagement.

### 📊 6. Financial Learning Dashboard
- Monitor savings progress.
- View user statistics.
- Track game performance and achievements.
- Access financial learning activities from one interface.

## 🛠️ Technologies Used

**Frontend**
- HTML5
- CSS3
- JavaScript
- Chart.js

**Backend**
- Python
- Flask
- Flask-SQLAlchemy
- OpenAI API

**Database**
- SQLite

**AI Integration**
- OpenAI GPT-4o-mini

**Development Tools**
- Visual Studio Code
- Git
- GitHub

## 🏗️ System Architecture

DuitSmart follows a Flask-based web application architecture:

1. **Presentation Layer:** HTML, CSS, and JavaScript provide the interactive user interface.
2. **Application Layer:** Flask handles application logic, API requests, and user interactions.
3. **AI Integration Layer:** OpenAI API powers the financial literacy chatbot.
4. **Database Layer:** SQLite and Flask-SQLAlchemy manage user profiles, savings goals, conversations, and game history.

## 📂 Project Structure

```text
DuitSmart/
│
├── duitsmart_app.py       # Main Flask application
├── app.env                # Environment variables
│
├── instance/
│   └── duitsmart.db      # SQLite database
│
├── static/                # Static assets
│
└── templates/
    └── duitsmart.html    # Main application interface
```

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/nuraliahatikah/DuitSmart.git
```

### 2. Navigate to the Project Folder

```bash
cd DuitSmart
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install flask flask-sqlalchemy openai python-dotenv
```

### 5. Configure Environment Variables

Create an `app.env` file in the project root directory:

```env
OPENAI_API_KEY=your_openai_api_key
```

Replace `your_openai_api_key` with your own OpenAI API key.

**Important:** Never upload your API key or actual environment file to GitHub. Add `app.env` to `.gitignore` and provide an `app.env.example` template instead.

### 6. Run the Application

```bash
python duitsmart_app.py
```

### 7. Access the Application

Open your browser and navigate to:

```text
http://127.0.0.1:5000
```

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat` | AI chatbot interaction |
| GET | `/api/goals` | Retrieve savings goals |
| POST | `/api/goals` | Create a savings goal |
| POST | `/api/goals/<id>/add` | Add savings contribution |
| DELETE | `/api/goals/<id>` | Delete a savings goal |
| POST | `/api/game/complete` | Record game completion |
| GET | `/api/user/data` | Retrieve user statistics |
| GET | `/api/leaderboard` | Retrieve leaderboard |
| POST | `/api/conversation/clear` | Clear conversation history |
| POST | `/api/reset` | Reset user data |
| GET | `/api/achievements` | Retrieve achievements |

## 🎯 Project Objectives

- To promote financial literacy among Malaysian teenagers.
- To provide accessible financial guidance through an AI-powered chatbot.
- To encourage responsible saving and spending habits.
- To make financial education more engaging through gamification.
- To develop practical money management skills through interactive learning experiences.

## 🌟 Project Highlights

- AI-powered financial education chatbot.
- Interactive financial literacy games.
- Personalized savings goal tracking.
- Gamification with points, coins, and achievements.
- Integrated financial learning dashboard.
- Designed with Malaysian teenagers in mind.



---

*Empowering the next generation to make smarter financial decisions, one ringgit at a time! 💚*
