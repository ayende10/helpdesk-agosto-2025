from flask import Flask, render_template, request, redirect, url_for, flash, session 
import pymysql 
from werkzeug.security import generate_password_hash, check_password_hash 
from config import Config 
from functools import wraps 
app = Flask(__name__) 

app.config.from_object(Config) 

def get_db_connection():
    return pymysql.connect( 
        host=app.config["DB_HOST"], 
        user=app.config["DB_USER"], 
        password=app.config["DB_PASSWORD"], 
        database=app.config["DB_NAME"], 
        cursorclass=pymysql.cursors.DictCursor 
    ) 
 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function
 
 
def role_required(*roles): 
    def decorator(f): 
        @wraps(f) 
        def decorated_function(*args, **kwargs): 
            if "user_role" not in session or session["user_role"] not in roles: 
                flash("You do not have permission to access this page.", "danger") 
                return redirect(url_for("dashboard")) 
            return f(*args, **kwargs) 
        return decorated_function 
    return decorator
@app.route("/") 
def index(): 
    # If user is logged in, redirect to dashboard 
    if "user_id" in session: 
        return redirect(url_for("dashboard")) 
    return redirect(url_for("login")) 

@app.route("/login", methods=["GET", "POST"]) 
def login(): 
    if request.method == "POST": 
        email = request.form.get("email") 
        password = request.form.get("password") 
 
        conn = get_db_connection() 
        with conn.cursor() as cursor: 
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,)) 
            user = cursor.fetchone() 
        conn.close() 
 
        if user and check_password_hash(user["password_hash"], password):
             # Store user info in session 
            session["user_id"] = user["id"] 
            session["user_name"] = user["name"] 
            session["user_role"] = user["role"] 
            flash("Welcome, {}!".format(user["name"]), "success") 
            return redirect(url_for("dashboard")) 
        else: 
            flash("Invalid email or password.", "danger") 
 
    return render_template("login.html") 
 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            flash("All fields are required.", "warning")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (%s, %s, %s, 'USER')
            """, (name, email, password_hash))
            conn.commit()
        conn.close()

        flash("User registered successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")



@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db_connection()
    with conn.cursor() as cursor:

        # Tickets por estado
        cursor.execute("""
            SELECT status, COUNT(*) AS count
            FROM tickets
            GROUP BY status
        """)
        status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}

        open_tickets = status_counts.get("OPEN", 0)
        in_progress_tickets = status_counts.get("IN_PROGRESS", 0)
        resolved_tickets = status_counts.get("RESOLVED", 0)
        total_tickets = sum(status_counts.values())

        # Tickets por prioridad
        cursor.execute("""
            SELECT priority, COUNT(*) AS count
            FROM tickets
            GROUP BY priority
        """)
        priority_counts = {row["priority"]: row["count"] for row in cursor.fetchall()}

        low_priority = priority_counts.get("LOW", 0)
        medium_priority = priority_counts.get("MEDIUM", 0)
        high_priority = priority_counts.get("HIGH", 0)

        # Usuarios
        cursor.execute("""
            SELECT 
                COUNT(*) AS total_users,
                SUM(CASE WHEN role = 'AGENT' THEN 1 ELSE 0 END) AS total_agents
            FROM users
        """)
        users_data = cursor.fetchone()

        total_users = users_data["total_users"]
        total_agents = users_data["total_agents"]

    conn.close()

    return render_template(
        "dashboard.html",
        open_tickets=open_tickets,
        in_progress_tickets=in_progress_tickets,
        resolved_tickets=resolved_tickets,
        total_tickets=total_tickets,
        low_priority=low_priority,
        medium_priority=medium_priority,
        high_priority=high_priority,
        total_users=total_users,
        total_agents=total_agents
    )



@app.route("/logout") 
@login_required 
def logout(): 
    session.clear() 
    flash("You have been logged out.", "info") 
    return redirect(url_for("login")) 

@app.route("/tickets") 
@login_required 
def tickets_list(): 
    user_id = session["user_id"] 
    user_role = session["user_role"]
    conn = get_db_connection() 
    with conn.cursor() as cursor: 
        if user_role == "ADMIN": 
            cursor.execute(""" 
                SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name 
                FROM tickets t 
                JOIN users u ON t.created_by = u.id 
                LEFT JOIN users a ON t.assigned_to = a.id 
                ORDER BY t.created_at DESC 
            """) 
        elif user_role == "AGENT": 
            cursor.execute(""" 
                SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name 
                FROM tickets t 
                JOIN users u ON t.created_by = u.id 
                LEFT JOIN users a ON t.assigned_to = a.id 
                WHERE t.assigned_to = %s OR t.assigned_to IS NULL 
                ORDER BY t.created_at DESC 
            """, (user_id,)) 
        else:  # USER 
            cursor.execute(""" 
                SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name 
                FROM tickets t 
                JOIN users u ON t.created_by = u.id 
                LEFT JOIN users a ON t.assigned_to = a.id 
                WHERE t.created_by = %s 
                ORDER BY t.created_at DESC 
            """, (user_id,)) 
 
        tickets = cursor.fetchall() 
    conn.close() 
 
    return render_template("tickets_list.html", tickets=tickets) 

@app.route("/tickets/new", methods=["GET", "POST"]) 
@login_required
def ticket_new(): 
    if request.method == "POST": 
        title = request.form.get("title") 
        description = request.form.get("description") 
        priority = request.form.get("priority") 
        created_by = session["user_id"] 
 
        if not title or not description: 
            flash("Title and description are required.", "warning") 
            return redirect(url_for("ticket_new")) 
 
        conn = get_db_connection() 
        with conn.cursor() as cursor: 
            cursor.execute(""" 
                INSERT INTO tickets (title, description, priority, created_by) 
                VALUES (%s, %s, %s, %s) 
            """, (title, description, priority, created_by)) 
        conn.commit() 
        conn.close() 
 
        flash("Ticket created successfully.", "success") 
        return redirect(url_for("tickets_list")) 
 
    return render_template("ticket_new.html") 

@app.route("/tickets/<int:ticket_id>", methods=["GET", "POST"]) 
@login_required 
def ticket_detail(ticket_id): 
    conn = get_db_connection() 
    with conn.cursor() as cursor: 
        cursor.execute(""" 
            SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name 
            FROM tickets t 
            JOIN users u ON t.created_by = u.id 
            LEFT JOIN users a ON t.assigned_to = a.id 
            WHERE t.id = %s 
        """, (ticket_id,)) 
        ticket = cursor.fetchone() 
 
        cursor.execute(""" 
            SELECT c.*, u.name AS user_name 
            FROM ticket_comments c 
            JOIN users u ON c.user_id = u.id 
            WHERE c.ticket_id = %s 
            ORDER BY c.created_at ASC 
        """, (ticket_id,)) 
        comments = cursor.fetchall() 
 
        cursor.execute("SELECT id, name FROM users WHERE role IN ('ADMIN', 'AGENT')") 
    agents = cursor.fetchall() 
    conn.close() 
 
    if not ticket: 
        flash("Ticket not found.", "danger") 
        return redirect(url_for("tickets_list")) 
 
    return render_template("ticket_detail.html", 
                           ticket=ticket, 
                           comments=comments, 
                           agents=agents) 

@app.route("/tickets/<int:ticket_id>/update", methods=["POST"]) 
@login_required 
def ticket_update(ticket_id): 
    user_role = session["user_role"] 
    if user_role not in ["ADMIN", "AGENT"]: 
        flash("You are not allowed to update tickets.", "danger") 
        return redirect(url_for("ticket_detail", ticket_id=ticket_id)) 
 
    status = request.form.get("status") 
    assigned_to = request.form.get("assigned_to") or None 
 
    conn = get_db_connection() 
    with conn.cursor() as cursor: 
        cursor.execute(""" 
            UPDATE tickets 
            SET status = %s, assigned_to = %s 
            WHERE id = %s 
        """, (status, assigned_to, ticket_id)) 
    conn.commit() 
    conn.close() 
 
    flash("Ticket updated.", "success") 
    return redirect(url_for("ticket_detail", ticket_id=ticket_id)) 
 
 
@app.route("/tickets/<int:ticket_id>/comments", methods=["POST"]) 
@login_required 
def comment_add(ticket_id): 
    comment_text = request.form.get("comment") 
    user_id = session["user_id"] 
 
    if not comment_text: 
        flash("Comment cannot be empty.", "warning") 
        return redirect(url_for("ticket_detail", ticket_id=ticket_id)) 
 
    conn = get_db_connection() 
    with conn.cursor() as cursor: 
        cursor.execute(""" 
            INSERT INTO ticket_comments (ticket_id, user_id, comment) 
            VALUES (%s, %s, %s) 
        """, (ticket_id, user_id, comment_text)) 
    conn.commit() 
    conn.close() 
 
    flash("Comment added.", "success") 
    return redirect(url_for("ticket_detail", ticket_id=ticket_id)) 

@app.route("/users") 
@login_required 
@role_required("ADMIN") 
def users_list(): 
    conn = get_db_connection() 
    with conn.cursor() as cursor: 
        cursor.execute("SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC") 
        users = cursor.fetchall() 
    conn.close() 
    return render_template("users_list.html", users=users)

@app.route("/users/<int:user_id>/role", methods=["POST"]) 
@login_required 
@role_required("ADMIN") 
def user_change_role(user_id): 
    new_role = request.form.get("role") 
    if new_role not in ["ADMIN", "AGENT", "USER"]: 
        flash("Invalid role.", "danger") 
        return redirect(url_for("users_list")) 
 
    conn = get_db_connection() 
    with conn.cursor() as cursor: 
        cursor.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id)) 
    conn.commit() 
    conn.close() 
 
    flash("Role updated.", "success") 
    return redirect(url_for("users_list"))  
 
 
if __name__ == "__main__": 
    app.run(debug=True) 