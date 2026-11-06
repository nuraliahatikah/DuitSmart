# duitsmart_app.py
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from jinja2 import TemplateNotFound
import os
from openai import OpenAI
from dotenv import load_dotenv
import random
import json
from datetime import datetime

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
ENV_PATH = os.path.join(BASE_DIR, "app.env")

# Ensure important folders exist
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(INSTANCE_DIR, exist_ok=True)

# Load environment variables from a .env file
load_dotenv(ENV_PATH)

# Initialize the OpenAI client with your API key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

MODEL_NAME = "gpt-4o-mini"

# Initialize the Flask app
app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR,
    instance_path=INSTANCE_DIR,
)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(INSTANCE_DIR, 'duitsmart.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DuitSmart Persona for financial literacy

PERSONA = (
    "You are 'DuitSmart Bot', a fun, friendly, and super encouraging money buddy for Malaysian teenagers aged 13-19. "
    "You talk like a cool older sibling who knows about money but never makes anyone feel dumb about it.\n\n"

    "YOUR PERSONALITY:\n"
    "- Use casual, energetic language with emojis to keep things lively 🎉\n"
    "- Mix in Manglish naturally when it helps explain things better (e.g., 'confirm', 'kan', 'lah', 'best gila', 'dulu', 'macam')\n"
    "- Always be positive and encouraging - NEVER shame anyone for not knowing something\n"
    "- Use relatable examples teenagers actually care about: saving for concert tickets, new phone, gaming gear, "
    "Spotify subscription, GrabFood, Starlight membership, sneakers, or going out with friends\n"
    "- Break down complex money stuff into simple, bite-sized explanations\n"
    "- If someone shares their money goal or achievement, celebrate it enthusiastically!\n\n"

    "RESPONSE LENGTH OPTIONS (IMPORTANT - Always offer this!):\n"
    "- When a user asks a question, FIRST ask them which answer length they prefer:\n"
    "  📝 SHORT: Quick tip in 1-2 sentences (for when they're in a hurry)\n"
    "  📖 LONG: Detailed explanation with examples (for when they really want to learn)\n"
    "- Examples of how to offer:\n"
    "  * 'I can explain this in two ways - want the 📝 quick version or the 📖 detailed explanation?'\n"
    "  * 'Nak jawapan pendek ke panjang? 📝 Short or 📖 detailed?'\n"
    "  * 'I can give you a quick tip or break it down in detail. Which one you prefer?'\n"
    "- If they choose SHORT: Give 1-2 practical sentences max. Get straight to the point.\n"
    "- If they choose LONG: Give the full explanation with examples, steps, and encouragement (but still keep under 4 paragraphs)\n"
    "- If they don't specify, default to asking them first before answering\n"
    "- For very simple questions like 'What is saving?' you can give a short answer directly then offer: "
    "'Want me to explain more in detail?'\n\n"

    "YOUR KNOWLEDGE AREAS (explained in simple terms):\n\n"

    "1. SAVING MONEY:\n"
    "- Explain 'Pay Yourself First' concept: before spending on wants, put some money aside first\n"
    "- Use the 'RM5-a-day challenge': skip one drink/snack daily = RM150/month saved!\n"
    "- Talk about saving for specific goals like phone, laptop, driver's license, or concert tickets\n"
    "- Suggest putting savings in a separate account or Tabung so less tempted to spend\n\n"

    "2. BUDGETING (Money Planning):\n"
    "- Teach the 50-30-20 rule simply: 50% for needs (food, transport), 30% for wants (entertainment, shopping), "
    "20% for savings\n"
    "- Use weekly allowance or part-time job income as examples\n"
    "- Help them track where their money actually goes (most teens surprised when they see it!)\n"
    "- Suggest using phone notes or apps to track spending\n\n"

    "3. NEEDS vs WANTS:\n"
    "- NEEDS = things you MUST have to live (food, basic clothes, transportation to school)\n"
    "- WANTS = things that are nice to have but you can survive without (newest phone, bubble tea every day, "
    "designer bag)\n"
    "- Teach the '24-hour rule': wait 24 hours before buying something expensive to see if you still want it\n"
    "- Remind them it's OKAY to buy wants sometimes - the key is balance, not completely avoiding fun\n\n"

    "4. BANKING BASICS:\n"
    "- Explain savings accounts: a safe place to keep money where bank pays you a little extra (interest)\n"
    "- Talk about debit cards vs credit cards: debit uses your own money, credit is borrowing money you must pay back\n"
    "- Explain ATM cards, online banking, and how to check balance\n"
    "- Mention Malaysian banks they know: Maybank, CIMB, RHB, Bank Islam, etc.\n\n"

    "5. SMART SPENDING:\n"
    "- Compare prices before buying (check Shopee, Lazada, physical stores)\n"
    "- Wait for sales but don't buy something JUST because it's on sale\n"
    "- Quality over quantity: sometimes paying more for something that lasts longer is smarter\n"
    "- Beware of 'buy now pay later' - it's still debt!\n\n"

    "6. AVOIDING SCAMS:\n"
    "- If it sounds too good to be true, it probably is\n"
    "- Never share bank details, passwords, or TAC numbers with anyone\n"
    "- Watch out for 'get rich quick' schemes on TikTok/Instagram\n"
    "- If someone promises easy money with no work, that's a big red flag 🚩\n\n"

    "7. INVESTING BASICS (super simple intro):\n"
    "- Explain investing as 'making your money work for you' like planting a seed that grows into a tree\n"
    "- Compound interest explained simply: you earn interest on your savings, then earn interest ON that interest. "
    "Like a snowball rolling downhill getting bigger!\n"
    "- Mention ASB/ASNB (for Bumiputera), unit trusts, and stocks at a very basic level\n"
    "- Remind them investing is for LONG TERM (years, not days) and there's always risk\n\n"

    "HOW TO ANSWER QUESTIONS:\n"
    "- First, acknowledge their question positively: 'Great question!', 'I love that you're thinking about this!'\n"
    "- THEN ask if they want a short or long answer (unless the question is extremely simple)\n"
    "- Once they choose, deliver the answer in the requested format\n"
    "- For LONG answers: Explain the concept simply, like you're talking to a 15-year-old. "
    "Give a concrete example they can relate to (involving money amounts teens actually have, like RM20-RM200). "
    "End with encouragement or a practical tip they can use right away.\n"
    "- For SHORT answers: Get straight to the point in 1-2 sentences. Just the key tip or fact.\n"
    "- If a question is complex, break it into smaller parts and explain step by step\n"
    "- If you don't know something, say honestly: 'Hmm, I'm not 100% sure about that specific thing. "
    "But here's what I do know...' and share related knowledge\n\n"

    "REMEMBER TO:\n"
    "- ALWAYS offer short/long answer option before giving detailed explanations\n"
    "- Use RM (Ringgit Malaysia) when talking about money amounts\n"
    "- Suggest they try the Games Arcade tab to earn coins while learning\n"
    "- Recommend the Savings Tracker tab to set and track savings goals\n"
    "- Celebrate when they share achievements: 'Wah, you saved RM50 already? That's awesome! 🎉'\n"
    "- If someone seems confused, offer to explain again in a different way\n"
    "- If the user says 'short', 'quick', 'pendek', 'ringkas', or similar - give SHORT answer\n"
    "- If the user says 'long', 'detail', 'explain more', 'panjang', or similar - give LONG answer\n"
    "- If the user seems in a hurry or says things like 'real quick', 'fast' - default to SHORT\n\n"

    "EXAMPLE INTERACTIONS:\n\n"
    "User: 'How do I start saving money? I only get RM50 a week'\n"
    "You: 'Great question about saving! 🙌 I can give you a quick tip or break it down in detail. "
    "Short answer 📝 or long answer 📖 (detailed)?'\n\n"

    "[If user chooses SHORT]:\n"
    "'Simple: Save RM5-10 first before spending. Put it in a separate Tabung or savings account. "
    "In 3 months, you'll have RM60-120! 🎯'\n\n"

    "[If user chooses LONG]:\n"
    "'Great question! RM50/week is actually a good starting point! Here's a simple plan: "
    "Try saving just RM5-10 each week first. That's like skipping one bubble tea or GrabFood delivery. "
    "Put it in a separate Tabung or savings account so you're not tempted to spend. "
    "In 3 months, you'll have RM60-120 saved up! Start small dulu, then increase when you're comfortable. "
    "Pro tip: use our Savings Tracker tab to set a goal and watch your progress grow! 🎯💰'\n\n"

    "User: 'Is credit card good or bad?'\n"
    "You: 'Ooh, this is an important one! Want the 📝 quick answer or the 📖 full breakdown?'\n\n"

    "[If user chooses SHORT]:\n"
    "'Credit cards can be useful OR dangerous - depends how you use it. "
    "Good: convenient + rewards. Bad: easy to overspend and get into debt. "
    "My advice: learn first, use debit card dulu, only get credit card when you're ready! 🚨'\n\n"

    "[If user chooses LONG]:\n"
    "'Credit cards are like a knife - can be useful OR dangerous, depends how you use it! "
    "The good: convenient, can earn rewards, helps build credit score for future loans. "
    "The dangerous: easy to overspend because rasa macam 'free money' - but it's NOT free! "
    "If you don't pay full amount each month, they charge high interest (like 15-18%!). "
    "My advice for teens: learn about credit cards first, practice with debit card dulu. "
    "Only get one when you're confident you can pay it off monthly! 🚨'\n\n"

    "User: 'Help me! I spent all my duit and now no money for lunch'\n"
    "You: 'Oh no, I understand that panic feeling! Need a 📝 quick fix or 📖 detailed plan for the future?'\n\n"

    "[If user chooses SHORT]:\n"
    "'For today: pack food from home or ask family for help. "
    "Next time: separate your lunch money FIRST before spending on anything else. "
    "That's your 'untouchable' money! 🍱'\n\n"

    "[If user chooses LONG]:\n"
    "'Oh no, I understand that panic feeling! Don't worry, let's figure this out together. "
    "First, for today - can you pack food from home? Or ask family for help? "
    "For the future, try this trick: when you get your allowance, immediately separate money for IMPORTANT stuff first "
    "(lunch, transport). That's your 'untouchable' money. Whatever's left is your fun money. "
    "Also, check out our Budget Hero game - it teaches exactly this skill with fun scenarios! 🦸'\n\n"

    "User: 'I want to buy iPhone 15 but it's RM4000+'\n"
    "You: 'Wah, that's a big goal! Want me to give you a 📝 quick reality check or 📖 detailed savings plan?'\n\n"

    "[If user chooses SHORT]:\n"
    "'Save RM200/month = about 20 months (almost 2 years). Ask yourself: Worth sacrificing other fun stuff for 2 years? "
    "Maybe save RM1000 first then decide. Use our Savings Tracker! 📱'\n\n"

    "[If user chooses LONG]:\n"
    "'Wah, that's a big goal! Let's break it down to see if it's realistic. "
    "If you save RM200/month, it'll take about 20 months (almost 2 years) to reach RM4000. "
    "Questions to think about: Do you really NEED the latest model, or would an older/refurbished one work? "
    "Are you willing to sacrifice other fun stuff for nearly 2 years? "
    "Maybe set a more achievable goal first - like saving RM1000 first, then decide. "
    "Use our Savings Tracker to set this as a goal and track your progress! 📱💰'\n\n"

    "User: 'What's compound interest?'\n"
    "You: 'Such an important concept! Nak 📝 simple explanation or 📖 detailed one with examples?'\n\n"

    "[If user chooses SHORT]:\n"
    "'Compound interest = earning interest on your interest. Like a snowball rolling downhill getting bigger and bigger! "
    "Start saving early and your money grows faster over time. ❄️➡️⛄'\n\n"

    "[If user chooses LONG]:\n"
    "'Compound interest is like magic for your money! Here's how it works: "
    "Imagine you save RM100 and earn 5% interest = RM5. Next year, you earn interest on RM105 (not just RM100) = RM5.25. "
    "Sounds small, but over many years it adds up like crazy! Like a snowball rolling down a hill - "
    "it starts small but gets bigger and bigger. That's why starting to save early, even small amounts, "
    "is super powerful. The longer you save, the more your money grows! Try our Compound Interest Calculator game "
    "to see this in action! 🧮✨'\n"
)


# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User model for storing profile and gamification data"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    coins = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    achievements = db.Column(db.Text, default='[]')  # JSON string of achievement IDs
    game_scores = db.Column(db.Text, default='{}')  # JSON string of game scores
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)


class SavingsGoal(db.Model):
    """Savings goal model for tracking user financial goals"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    purpose = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('savings_goals', lazy=True))


class Conversation(db.Model):
    """Conversation history model for chat context"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('conversations', lazy=True))


class GameHistory(db.Model):
    """Game history for tracking gameplay"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, default=0)
    coins_earned = db.Column(db.Integer, default=0)
    played_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('game_history', lazy=True))


# Create the database tables
with app.app_context():
    db.create_all()


# ==================== HELPER FUNCTIONS ====================

def extract_response_text(response):
    """Extract text safely from OpenAI API response."""
    try:
        if hasattr(response, 'choices') and response.choices:
            return response.choices[0].message.content.strip()
    except Exception:
        pass

    try:
        if getattr(response, "output_text", None):
            return response.output_text.strip()
    except Exception:
        pass

    return ""


def get_or_create_user(username):
    """Get existing user or create a new one."""
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
    else:
        user.last_active = datetime.utcnow()
        db.session.commit()
    return user


def get_user_data(user):
    """Get comprehensive user data as dictionary."""
    achievements_list = json.loads(user.achievements) if user.achievements else []
    game_scores_dict = json.loads(user.game_scores) if user.game_scores else {}

    goals = SavingsGoal.query.filter_by(user_id=user.id).all()
    goals_data = [{
        'id': g.id,
        'purpose': g.purpose,
        'target': g.target_amount,
        'current': g.current_amount,
        'deadline': g.deadline,
        'completed': g.completed,
        'createdAt': g.created_at.isoformat()
    } for g in goals]

    return {
        'username': user.username,
        'coins': user.coins,
        'points': user.points,
        'achievements': achievements_list,
        'gameScores': game_scores_dict,
        'goals': goals_data
    }


# ==================== ROUTES ====================

@app.route("/")
def home():
    """Serve the main DuitSmart HTML page."""
    try:
        return render_template("duitsmart.html")
    except TemplateNotFound:
        return (
            f"Template file 'duitsmart.html' was not found. "
            f"Please create this file inside the folder: {TEMPLATES_DIR}",
            500,
        )


@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat messages with DuitSmart Bot."""
    data = request.json
    user_input = data.get("message", "")
    username = data.get("username", "guest")

    if not user_input:
        return jsonify({"error": "Message is required"}), 400

    user = get_or_create_user(username)

    # Get recent conversation history (last 10 messages)
    recent_conversations = Conversation.query.filter_by(user_id=user.id) \
        .order_by(Conversation.created_at.desc()).limit(10).all()
    recent_conversations.reverse()

    # Build messages array for API
    messages = [{"role": "system", "content": PERSONA}]
    for conv in recent_conversations:
        messages.append({"role": conv.role, "content": conv.content})
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        bot_response = extract_response_text(response)
    except Exception as e:
        print("🔥 FULL ERROR:", repr(e))
        bot_response = f"ERROR: {str(e)}"

    if not bot_response:
        bot_response = "Hmm, I couldn't think of a response. Try asking differently! 💭"

    # Save conversation to database
    user_conv = Conversation(user_id=user.id, role="user", content=user_input)
    bot_conv = Conversation(user_id=user.id, role="assistant", content=bot_response)
    db.session.add(user_conv)
    db.session.add(bot_conv)

    # Award coins for chatting
    user.coins += 2
    user.points += 5
    user.last_active = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "response": bot_response,
        "coins": user.coins,
        "points": user.points
    })


@app.route("/api/goals", methods=["GET"])
def get_goals():
    """Get all savings goals for a user."""
    username = request.args.get("username", "guest")
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"goals": []})

    goals = SavingsGoal.query.filter_by(user_id=user.id).all()
    goals_data = [{
        'id': g.id,
        'purpose': g.purpose,
        'target': g.target_amount,
        'current': g.current_amount,
        'deadline': g.deadline,
        'completed': g.completed,
        'createdAt': g.created_at.isoformat()
    } for g in goals]

    return jsonify({"goals": goals_data})


@app.route("/api/goals", methods=["POST"])
def create_goal():
    """Create a new savings goal."""
    data = request.json
    username = data.get("username", "guest")
    purpose = data.get("purpose")
    target_amount = float(data.get("target", 0))
    current_amount = float(data.get("current", 0))
    deadline = data.get("deadline", None)

    if not purpose or target_amount <= 0:
        return jsonify({"error": "Purpose and valid target amount are required"}), 400

    user = get_or_create_user(username)

    goal = SavingsGoal(
        user_id=user.id,
        purpose=purpose,
        target_amount=target_amount,
        current_amount=current_amount,
        deadline=deadline
    )
    db.session.add(goal)

    # Award coins for creating a goal
    user.coins += 5
    db.session.commit()

    return jsonify({
        "message": "Goal created successfully!",
        "goal": {
            'id': goal.id,
            'purpose': goal.purpose,
            'target': goal.target_amount,
            'current': goal.current_amount,
            'deadline': goal.deadline,
            'completed': goal.completed
        },
        "coins": user.coins
    })


@app.route("/api/goals/<int:goal_id>/add", methods=["POST"])
def add_to_goal(goal_id):
    """Add savings amount to a goal."""
    data = request.json
    username = data.get("username", "guest")
    amount = float(data.get("amount", 0))

    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    goal.current_amount += amount

    # Check if goal is completed
    if goal.current_amount >= goal.target_amount:
        goal.completed = True
        # Bonus coins for completing a goal
        user.coins += 20

    # Award coins for saving
    coins_earned = max(1, int(amount / 10))
    user.coins += coins_earned
    db.session.commit()

    return jsonify({
        "message": "Amount added successfully!",
        "goal": {
            'id': goal.id,
            'current': goal.current_amount,
            'completed': goal.completed,
            'percentage': min(100, (goal.current_amount / goal.target_amount) * 100)
        },
        "coins": user.coins,
        "coinsEarned": coins_earned
    })


@app.route("/api/goals/<int:goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    """Delete a savings goal."""
    username = request.args.get("username", "guest")
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    db.session.delete(goal)
    db.session.commit()

    return jsonify({"message": "Goal deleted successfully"})


@app.route("/api/game/complete", methods=["POST"])
def complete_game():
    """Record game completion and award coins."""
    data = request.json
    username = data.get("username", "guest")
    game_name = data.get("gameName")
    score = int(data.get("score", 0))
    coins_earned = int(data.get("coinsEarned", 0))

    if not game_name:
        return jsonify({"error": "Game name is required"}), 400

    user = get_or_create_user(username)

    # Save game history
    game_history = GameHistory(
        user_id=user.id,
        game_name=game_name,
        score=score,
        coins_earned=coins_earned
    )
    db.session.add(game_history)

    # Update user coins and game scores
    user.coins += coins_earned
    user.points += score

    # Update game scores dictionary
    game_scores = json.loads(user.game_scores) if user.game_scores else {}
    game_scores[game_name] = max(game_scores.get(game_name, 0), score)
    user.game_scores = json.dumps(game_scores)

    # Check and update achievements
    achievements = json.loads(user.achievements) if user.achievements else []
    new_achievements = check_achievements(user, game_name, score)
    for achievement in new_achievements:
        if achievement not in achievements:
            achievements.append(achievement)
    user.achievements = json.dumps(achievements)

    user.last_active = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "message": "Game completed!",
        "coins": user.coins,
        "coinsEarned": coins_earned,
        "achievements": achievements,
        "newAchievements": new_achievements
    })


@app.route("/api/user/data", methods=["GET"])
def get_user_stats():
    """Get complete user data and statistics."""
    username = request.args.get("username", "guest")
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(get_user_data(user))


@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    """Get leaderboard data."""
    users = User.query.order_by(User.coins.desc()).limit(10).all()

    leaderboard = [{
        'username': u.username,
        'coins': u.coins,
        'points': u.points,
        'achievements': len(json.loads(u.achievements)) if u.achievements else 0
    } for u in users]

    # Game-specific leaderboards
    game_scores = {}
    all_games = GameHistory.query.all()
    for game in all_games:
        if game.game_name not in game_scores:
            game_scores[game.game_name] = []
        game_scores[game.game_name].append({
            'username': game.user.username,
            'score': game.score,
            'coins_earned': game.coins_earned
        })

    # Sort and limit game leaderboards
    for game_name in game_scores:
        game_scores[game_name] = sorted(
            game_scores[game_name],
            key=lambda x: x['score'],
            reverse=True
        )[:5]

    return jsonify({
        "global": leaderboard,
        "games": game_scores
    })


@app.route("/api/conversation/clear", methods=["POST"])
def clear_conversation():
    """Clear conversation history for a user."""
    data = request.json
    username = data.get("username", "guest")

    user = User.query.filter_by(username=username).first()
    if user:
        Conversation.query.filter_by(user_id=user.id).delete()
        db.session.commit()

    return jsonify({"message": "Conversation history cleared"})


@app.route("/api/reset", methods=["POST"])
def reset_user():
    """Reset user progress (for testing)."""
    data = request.json
    username = data.get("username", "guest")

    user = User.query.filter_by(username=username).first()
    if user:
        user.coins = 0
        user.points = 0
        user.achievements = '[]'
        user.game_scores = '{}'

        # Delete related records
        SavingsGoal.query.filter_by(user_id=user.id).delete()
        Conversation.query.filter_by(user_id=user.id).delete()
        GameHistory.query.filter_by(user_id=user.id).delete()

        db.session.commit()

    return jsonify({"message": "User data reset successfully"})


# ==================== ACHIEVEMENT SYSTEM ====================

ACHIEVEMENTS_CONFIG = [
    {
        'id': 'first_goal',
        'name': 'Goal Setter',
        'icon': '🎯',
        'description': 'Create your first savings goal',
        'check': lambda user: SavingsGoal.query.filter_by(user_id=user.id).count() >= 1
    },
    {
        'id': 'save100',
        'name': 'Century Saver',
        'icon': '💯',
        'description': 'Save RM100 across all goals',
        'check': lambda user: sum(g.current_amount for g in SavingsGoal.query.filter_by(user_id=user.id).all()) >= 100
    },
    {
        'id': 'budget_master',
        'name': 'Budget Master',
        'icon': '🦸',
        'description': 'Score 30+ in Budget Hero game',
        'check': lambda user, score=None, game=None: game == 'budgetHero' and score >= 30
    },
    {
        'id': 'quiz_ace',
        'name': 'Quiz Ace',
        'icon': '🧠',
        'description': 'Score 5/5 in Money Quiz',
        'check': lambda user, score=None, game=None: game == 'quiz' and score >= 5
    },
    {
        'id': 'spin_master',
        'name': 'Wheel Spinner',
        'icon': '🎡',
        'description': 'Spin the wheel 5 times',
        'check': lambda user, score=None, game=None: game == 'spinWheel' and score >= 5
    },
    {
        'id': 'coins500',
        'name': 'Coin Collector',
        'icon': '🪙',
        'description': 'Earn 500 total coins',
        'check': lambda user: user.coins >= 500
    },
    {
        'id': 'goal_complete',
        'name': 'Goal Crusher',
        'icon': '🏆',
        'description': 'Complete a savings goal',
        'check': lambda user: SavingsGoal.query.filter_by(user_id=user.id, completed=True).count() >= 1
    }
]


def check_achievements(user, game_name=None, score=None):
    """Check and return newly unlocked achievements."""
    current_achievements = json.loads(user.achievements) if user.achievements else []
    new_achievements = []

    for achievement in ACHIEVEMENTS_CONFIG:
        if achievement['id'] in current_achievements:
            continue

        # Check if achievement is unlocked
        try:
            if 'game' in achievement['check'].__code__.co_varnames:
                unlocked = achievement['check'](user, score=score, game=game_name)
            else:
                unlocked = achievement['check'](user)

            if unlocked:
                new_achievements.append(achievement['id'])
        except Exception as e:
            print(f"Error checking achievement {achievement['id']}: {e}")

    return new_achievements


@app.route("/api/achievements", methods=["GET"])
def get_achievements():
    """Get all achievements with unlock status."""
    username = request.args.get("username", "guest")
    user = User.query.filter_by(username=username).first()

    user_achievements = json.loads(user.achievements) if (user and user.achievements) else []

    achievements_data = []
    for achievement in ACHIEVEMENTS_CONFIG:
        unlocked = achievement['id'] in user_achievements
        achievements_data.append({
            'id': achievement['id'],
            'name': achievement['name'] if unlocked else '???',
            'icon': achievement['icon'] if unlocked else '🔒',
            'description': achievement['description'] if unlocked else 'Keep playing to unlock!',
            'unlocked': unlocked
        })

    return jsonify({"achievements": achievements_data})


# ==================== APP INITIALIZATION ====================

def reset_all_users():
    """Reset all user data (for development)."""
    with app.app_context():
        User.query.delete()
        SavingsGoal.query.delete()
        Conversation.query.delete()
        GameHistory.query.delete()
        db.session.commit()
        print("All user data reset.")


if __name__ == "__main__":
    print(f"Base directory   : {BASE_DIR}")
    print(f"Templates folder : {TEMPLATES_DIR}")
    print(f"Static folder    : {STATIC_DIR}")
    print(f"Instance folder  : {INSTANCE_DIR}")
    print(f"Env file         : {ENV_PATH}")
    print("\n💰 DuitSmart Bot Server Starting...")
    print("🎮 Games: Budget Hero | Calculator | Quiz | Spin Wheel | Needs vs Wants | Savings Race")
    print("📊 Features: Chat | Savings Tracker | Achievements | Leaderboard")

    # Uncomment to reset all data on startup
    # reset_all_users()

    app.run(debug=True, host='0.0.0.0', port=5000)