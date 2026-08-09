from flask import *
from database import *
from datetime import datetime, timedelta
import re
import qrcode
import os
from functools import wraps

user_table()
insert_default_admin()
create_members_table()
create_membership_table()
create_member_membership_table()
create_payments_table()
create_attendance_table()

app = Flask(__name__)
app.secret_key = 'gym-secret-key'

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'admin' not in session:
            flash("Please login as Admin.","warning")
            return redirect(url_for('index'))

        return f(*args, **kwargs)

    return decorated_function

def member_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'member_id' not in session:
            flash("Please login as Member.","warning")
            return redirect(url_for('index'))

        return f(*args, **kwargs)

    return decorated_function

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_member_qr(member_id):

    folder = os.path.join(BASE_DIR, "static", "qr_codes")

    os.makedirs(folder, exist_ok=True)

    filename = f"member_{member_id}.png"

    filepath = os.path.join(folder, filename)

    qr = qrcode.make(f"MEMBER_{member_id}")

    qr.save(filepath)

    return f"qr_codes/{filename}"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email'].strip()
        password = request.form['password'].strip()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT * FROM users WHERE email=? AND password=?',
            (email, password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session['admin'] = user['email']
            session['admin_name'] = user['name'] if 'name' in user.keys() else "Admin"
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid email or password', 'danger')

    return render_template('login.html')


@app.route('/dashboard')
@admin_required
def dashboard():

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    # Auto update expired memberships
    cur.execute("""
        UPDATE member_membership
        SET status='Expired'
        WHERE end_date < DATE('now')
          AND status='Active'
    """)

    conn.commit()

    # Total members
    cur.execute("SELECT COUNT(*) AS total FROM members")
    total_members = cur.fetchone()['total']

    # Active members
    cur.execute("SELECT COUNT(*) AS active FROM members WHERE status='Active'")
    active_members = cur.fetchone()['active']

    # Inactive members
    cur.execute("SELECT COUNT(*) AS inactive FROM members WHERE status='Inactive'")
    inactive_members = cur.fetchone()['inactive']

    # Expired memberships
    cur.execute("""
        SELECT COUNT(*) AS expired
        FROM member_membership
        WHERE status='Expired'
    """)

    expired_memberships = cur.fetchone()['expired']

    # Monthly Income
    cur.execute("""
        SELECT IFNULL(SUM(amount), 0) AS income
        FROM payments
        WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')
    """)

    monthly_income = cur.fetchone()['income']

    conn.close()

    return render_template(
        'dashboard.html',
        total_members=total_members,
        active_members=active_members,
        inactive_members=inactive_members,
        expired_memberships=expired_memberships,
        monthly_income=monthly_income
    )


@app.route('/logout')
@admin_required
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/add_member', methods=['GET', 'POST'])
@admin_required
def add_member():

    if request.method == 'POST':

        full_name = request.form['full_name'].strip()
        gender = request.form['gender']
        dob = request.form['dob']
        mobile = request.form['mobile'].strip()
        email = request.form['email'].strip()
        height = request.form['height']
        weight = request.form['weight']
        address = request.form['address'].strip()
        # Auto Generate Password from DOB
        password = datetime.strptime(
            dob,
            "%Y-%m-%d"
        ).strftime("%d%m%Y")

        # Mobile validation
        if not mobile.isdigit() or len(mobile) != 10:
            flash('Mobile number must be exactly 10 digits', 'warning')
            return render_template('add_member.html')

        # Email validation
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

        if email and not re.match(email_pattern, email):
            flash('Enter a valid email address', 'warning')
            return render_template('add_member.html')

        conn = get_connection()
        cur = conn.cursor()

        # Duplicate mobile
        cur.execute('SELECT * FROM members WHERE mobile=?', (mobile,))

        if cur.fetchone():
            conn.close()
            flash('Mobile number already exists', 'warning')
            return render_template('add_member.html')

        # Duplicate email
        if email:
            cur.execute('SELECT * FROM members WHERE email=?', (email,))

            if cur.fetchone():
                conn.close()
                flash('Email already exists', 'warning')
                return render_template('add_member.html')
            # Insert member
        cur.execute("""
            INSERT INTO members(
                full_name, gender, dob, mobile, email, password, height, weight, address
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ( full_name, gender, dob, mobile, email, password, height, weight, address
        ))

        # Last inserted member id
        member_id = cur.lastrowid

        # Generate QR Code
        qr_path = generate_member_qr(member_id)

        # Save QR path in database
        cur.execute("""
            UPDATE members
            SET qr_code=?
            WHERE member_id=?
        """, (qr_path, member_id))

        conn.commit()
        conn.close()

        flash(f"Member Added Successfully! Default Password: {password}","success")

        return redirect(url_for('view_members'))

    return render_template('add_member.html')

@app.route('/update_passwords')
@admin_required
def update_passwords():

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("SELECT member_id, dob FROM members")

    members = cur.fetchall()

    for member in members:

        if member['dob']:

            password = datetime.strptime(
                member['dob'],
                "%Y-%m-%d"
            ).strftime("%d%m%Y")

            cur.execute("""
                UPDATE members
                SET password=?
                WHERE member_id=?
            """, (password, member['member_id']))

    conn.commit()
    conn.close()

    return "Passwords Updated Successfully"

@app.route('/view_members')
@admin_required
def view_members():

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM members
        ORDER BY member_id DESC
    """)

    members = cur.fetchall()
    print("Total Members:", len(members))

    for m in members:
        print(dict(m))

    conn.close()

    return render_template('view_members.html', members=members)

@app.route('/search_member', methods=['GET', 'POST'])
@admin_required
def search_member():

    members = None   # change this

    if request.method == 'POST':

        keyword = request.form['keyword'].strip()

        conn = get_connection()
        conn.row_factory = sql.Row

        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM members
            WHERE full_name LIKE ? OR mobile LIKE ?
        """, (f'%{keyword}%', f'%{keyword}%'))

        members = cur.fetchall()

        conn.close()

    return render_template('search_member.html', members=members)

@app.route('/update_member/<int:id>', methods=['GET', 'POST'])
@admin_required
def update_member(id):

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute('SELECT * FROM members WHERE member_id=?', (id,))
    member = cur.fetchone()

    if request.method == 'POST':

        full_name = request.form['full_name'].strip()
        mobile = request.form['mobile'].strip()
        email = request.form['email'].strip()
        gender = request.form['gender']
        address = request.form['address'].strip()

        # Mobile validation
        if not mobile.isdigit() or len(mobile) != 10:
            flash('Mobile number must be exactly 10 digits', 'warning')
            return render_template('update_member.html', member=member)

        # Email validation
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

        if not re.match(email_pattern, email):
            flash('Enter a valid email address', 'warning')
            return render_template('update_member.html', member=member)

        cur.execute("""
            UPDATE members
            SET full_name=?,
                mobile=?,
                email=?,
                gender=?,
                address=?
            WHERE member_id=?
        """, (
            full_name,
            mobile,
            email,
            gender,
            address,
            id
        ))

        conn.commit()
        conn.close()

        flash('Member updated successfully!', 'success')

        return redirect(url_for('view_members'))

    conn.close()

    return render_template('update_member.html', member=member)

@app.route('/delete_member/<int:id>')
@admin_required
def delete_member(id):

    conn = get_connection()
    cur = conn.cursor()

    # Member inactive
    cur.execute("""
        UPDATE members
        SET status='Inactive'
        WHERE member_id=?
    """, (id,))

    print('Members updated:', cur.rowcount)

    # Membership inactive
    cur.execute("""
        UPDATE member_membership
        SET status='Inactive'
        WHERE member_id=? AND status='Active'
    """, (id,))

    print('Memberships updated:', cur.rowcount)

    conn.commit()
    conn.close()

    flash('Member and membership moved to inactive list', 'success')

    return redirect(url_for('view_members'))

@app.route('/add_plan', methods=['GET', 'POST'])
@admin_required
def add_plan():

    if request.method == 'POST':

        plan_name = request.form['plan_name'].strip()
        duration = request.form['duration']
        price = request.form['price']

        conn = get_connection()
        conn.row_factory = sql.Row
        cur = conn.cursor()

        # Duplicate plan check
        cur.execute(
            "SELECT * FROM membership_plan WHERE plan_name=?",
            (plan_name,)
        )

        if cur.fetchone():
            conn.close()
            flash("Membership plan already exists!", "warning")
            return render_template("add_plan.html")

        # Insert new plan
        cur.execute("""
            INSERT INTO membership_plan
            (plan_name, duration, price)
            VALUES (?, ?, ?)
        """, (plan_name, duration, price))

        conn.commit()
        conn.close()

        flash("Membership Plan Added Successfully!", "success")

        return redirect(url_for('view_plans'))

    return render_template("add_plan.html")

@app.route('/view_plans')
@admin_required
def view_plans():

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute('SELECT * FROM membership_plan')

    plans = cur.fetchall()

    conn.close()

    return render_template('view_plans.html', plans=plans)

@app.route('/assign_membership', methods=['GET', 'POST'])
@admin_required
def assign_membership():

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    # Active members
    cur.execute("SELECT member_id, full_name FROM members WHERE status='Active'")
    members = cur.fetchall()

    # Membership plans
    cur.execute("SELECT * FROM membership_plan")
    plans = cur.fetchall()

    if request.method == 'POST':

        member_id = request.form['member_id']
        plan_id = request.form['plan_id']

        # Check existing active membership
        cur.execute("""
            SELECT *
            FROM member_membership
            WHERE member_id=? AND status='Active'
        """, (member_id,))

        existing = cur.fetchone()

        if existing:
            conn.close()

            flash('This member already has an active membership!', 'warning')

            return redirect(url_for('assign_membership'))

        # Get plan duration
        cur.execute(
            'SELECT duration FROM membership_plan WHERE plan_id=?',
            (plan_id,)
        )

        plan = cur.fetchone()
        duration_days = plan['duration']

        start_date = datetime.today().date()
        end_date = start_date + timedelta(days=duration_days)

        # Insert membership
        cur.execute("""
            INSERT INTO member_membership(
                member_id,
                plan_id,
                start_date,
                end_date,
                status
            )
            VALUES (?, ?, ?, ?, 'Active')
        """, (
            member_id,
            plan_id,
            start_date,
            end_date
        ))

        conn.commit()
        conn.close()

        flash('Membership assigned successfully!', 'success')

        return redirect(url_for('view_member_memberships'))

    conn.close()

    return render_template(
        'assign_membership.html',
        members=members,
        plans=plans
    )

@app.route('/view_member_memberships')
@admin_required
def view_member_memberships():

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT mm.membership_id,
               m.full_name,
               mp.plan_name,
               mm.start_date,
               mm.end_date,
               mm.status
        FROM member_membership mm
        JOIN members m ON mm.member_id = m.member_id
        JOIN membership_plan mp ON mm.plan_id = mp.plan_id
        ORDER BY mm.membership_id DESC
    """)

    memberships = cur.fetchall()

    conn.close()

    return render_template(
        'view_member_memberships.html',
        memberships=memberships
    )

@app.route('/inactive_members')
@admin_required
def inactive_members():

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM members WHERE status='Inactive'")

    members = cur.fetchall()

    conn.close()

    return render_template('inactive_members.html', members=members)

@app.route('/restore_member/<int:id>')
@admin_required
def restore_member(id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE members SET status='Active' WHERE member_id=?", (id,))

    conn.commit()
    conn.close()

    flash('Member restored successfully!', 'success')

    return redirect(url_for('inactive_members'))

@app.route('/update_plan/<int:id>', methods=['GET', 'POST'])
@admin_required
def update_plan(id):

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    # Existing plan fetch
    cur.execute("SELECT * FROM membership_plan WHERE plan_id=?", (id,))
    plan = cur.fetchone()

    if plan is None:
        conn.close()
        flash("Membership plan not found!", "danger")
        return redirect('/view_plans')

    if request.method == 'POST':

        plan_name = request.form['plan_name']
        duration = request.form['duration']
        price = request.form['price']

        # Duplicate check
        cur.execute("""
            SELECT * FROM membership_plan
            WHERE plan_name=? AND plan_id != ?
        """, (plan_name, id))

        if cur.fetchone():
            flash("Plan name already exists!", "warning")
            conn.close()
            return redirect(f'/update_plan/{id}')

        cur.execute("""
            UPDATE membership_plan
            SET plan_name=?,
                duration=?,
                price=?
            WHERE plan_id=?
        """, (plan_name, duration, price, id))

        conn.commit()
        conn.close()

        flash("Membership Plan Updated Successfully!", "success")
        return redirect('/view_plans')

    conn.close()
    return render_template('update_plan.html', plan=plan)

@app.route('/delete_plan/<int:id>')
@admin_required
def delete_plan(id):

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    # Check if plan is assigned to any member
    cur.execute("""
        SELECT * FROM member_membership
        WHERE plan_id=?
    """, (id,))

    assigned = cur.fetchone()

    if assigned:
        flash("Cannot delete! This plan is already assigned to member(s).", "warning")
        conn.close()
        return redirect('/view_plans')

    # Delete plan
    cur.execute("""
        DELETE FROM membership_plan
        WHERE plan_id=?
    """, (id,))

    conn.commit()
    conn.close()

    flash("Membership Plan Deleted Successfully!", "success")

    return redirect('/view_plans')

@app.route('/receive_payment', methods=['GET', 'POST'])
@admin_required
def receive_payment():

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    # Active members only
    cur.execute("""
        SELECT member_id, full_name
        FROM members
        WHERE status='Active'
        ORDER BY full_name
    """)
    members = cur.fetchall()

    if request.method == 'POST':

        member_id = request.form['member_id']
        amount = request.form['amount']
        payment_mode = request.form['payment_mode']
        remarks = request.form['remarks']

        cur.execute("""
            INSERT INTO payments
            (member_id, amount, payment_mode, remarks)
            VALUES (?,?,?,?)
        """, (member_id, amount, payment_mode, remarks))

        conn.commit()
        conn.close()

        flash("Payment Received Successfully!", "success")
        return redirect('/payment_history')

    conn.close()

    return render_template(
        'receive_payment.html',
        members=members
    )

@app.route('/payment_history')
@admin_required
def payment_history():

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.payment_id,
            m.full_name,
            p.amount,
            p.payment_date,
            p.payment_mode,
            p.remarks
        FROM payments p
        JOIN members m
        ON p.member_id = m.member_id
        ORDER BY p.payment_date DESC
    """)

    payments = cur.fetchall()

    conn.close()

    return render_template(
        'payment_history.html',
        payments=payments
    )

@app.route('/delete_payment/<int:id>')
@admin_required
def delete_payment(id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM payments WHERE payment_id=?", (id,))

    conn.commit()
    conn.close()

    flash("Payment record deleted successfully!", "success")

    return redirect('/payment_history')

@app.route('/member_login', methods=['GET', 'POST'])
def member_login():

    if request.method == 'POST':

        mobile = request.form['mobile'].strip()
        password = request.form['password'].strip()

        conn = get_connection()
        conn.row_factory = sql.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM members
            WHERE mobile=?
            AND password=?
            AND status='Active'
        """, (mobile, password))

        member = cur.fetchone()

        conn.close()

        if member:

            session['member_id'] = member['member_id']
            session['member_name'] = member['full_name']

            flash("Login Successful", "success")

            return redirect(url_for('member_dashboard'))

        flash("Invalid Mobile Number or Password", "danger")

    return render_template("member_login.html")

@app.route('/member_dashboard')
@member_required
def member_dashboard():

    if 'member_id' not in session:
        return redirect(url_for('member_login'))

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    member_id = session['member_id']

    # Member Details
    cur.execute("""
        SELECT *
        FROM members
        WHERE member_id=?
    """, (member_id,))

    member = cur.fetchone()

    # Active Membership
    cur.execute("""
        SELECT
            mp.plan_name,
            mm.start_date,
            mm.end_date,
            mm.status
        FROM member_membership mm
        JOIN membership_plan mp
        ON mm.plan_id = mp.plan_id
        WHERE mm.member_id=?
        AND mm.status='Active'
    """, (member_id,))

    membership = cur.fetchone()

    # Last Payment
    cur.execute("""
        SELECT *
        FROM payments
        WHERE member_id=?
        ORDER BY payment_date DESC
        LIMIT 1
    """, (member_id,))

    payment = cur.fetchone()

    conn.close()

    return render_template(
        "member_dashboard.html",
        member=member,
        membership=membership,
        payment=payment
    )

@app.route('/member_logout')
@member_required
def member_logout():

    session.clear()

    flash("Logged Out Successfully", "success")

    return redirect(url_for('index'))

@app.route('/member_payment_history')
@member_required
def member_payment_history():

    if 'member_id' not in session:
        return redirect(url_for('member_login'))

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    member_id = session['member_id']

    # Active Membership
    cur.execute("""
        SELECT
            mp.plan_name,
            mp.price,
            mm.start_date,
            mm.end_date
        FROM member_membership mm
        JOIN membership_plan mp
        ON mm.plan_id = mp.plan_id
        WHERE mm.member_id=?
        AND mm.status='Active'
    """, (member_id,))

    membership = cur.fetchone()

    # Payment History
    cur.execute("""
        SELECT *
        FROM payments
        WHERE member_id=?
        ORDER BY payment_date DESC
    """, (member_id,))

    payments = cur.fetchall()

    # Total Paid
    cur.execute("""
        SELECT IFNULL(SUM(amount),0) total_paid
        FROM payments
        WHERE member_id=?
    """, (member_id,))

    total_paid = cur.fetchone()["total_paid"]

    if membership:

        total_amount = membership["price"]

        remaining = total_amount - total_paid

    else:

        total_amount = 0
        remaining = 0

    conn.close()

    print("Total Amount:", total_amount)
    print("Total Paid:", total_paid)
    print("Remaining:", remaining)
    print("Membership:", membership)

    return render_template(

        "member_payment_history.html",

        membership=membership,

        payments=payments,

        total_paid=total_paid,

        total_amount=total_amount,

        remaining=remaining

    )

@app.route('/member_payment')
@member_required
def member_payment():

    if 'member_id' not in session:
        return redirect(url_for('member_login'))

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    member_id = session['member_id']

    # Active Membership
    cur.execute("""
        SELECT
            mp.plan_name,
            mp.price
        FROM member_membership mm
        JOIN membership_plan mp
        ON mm.plan_id = mp.plan_id
        WHERE mm.member_id=?
        AND mm.status='Active'
    """, (member_id,))

    membership = cur.fetchone()

    # Total Paid
    cur.execute("""
        SELECT IFNULL(SUM(amount),0) total_paid
        FROM payments
        WHERE member_id=?
    """, (member_id,))

    total_paid = cur.fetchone()["total_paid"]

    remaining = membership["price"] - total_paid

    conn.close()

    return render_template(
        "member_payment.html",
        membership=membership,
        remaining=remaining
    )

@app.route('/member_pay_now', methods=['POST'])
@member_required
def member_pay_now():

    if 'member_id' not in session:
        return redirect(url_for('member_login'))

    member_id = session['member_id']

    amount = float(request.form['amount'])

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO payments(
            member_id,
            amount,
            payment_mode,
            remarks
        )
        VALUES(?,?,?,?)
    """,(member_id,
         amount,
         "Online",
         "Membership Fee Paid"))

    conn.commit()

    conn.close()

    flash("Payment Successful","success")

    return redirect(url_for('member_payment_history'))

@app.route('/member_attendance')
@member_required
def member_attendance():

    if 'member_id' not in session:
        return redirect(url_for('member_login'))

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    member_id = session['member_id']

    cur.execute("""
        SELECT
            attendance_date,
            check_in_time,
            latitude,
            longitude,
            location,
            status
        FROM attendance
        WHERE member_id=?
        ORDER BY attendance_date DESC,
                 check_in_time DESC
    """, (member_id,))

    attendance = cur.fetchall()

    conn.close()

    return render_template(
        "member_attendance.html",
        attendance=attendance
    )

@app.route('/mark_attendance')
@member_required
def mark_attendance():

    if 'member_id' not in session:
        return redirect(url_for('member_login'))

    member_id = session['member_id']

    lat = request.args.get("lat", "")
    lng = request.args.get("lng", "")
    location = request.args.get("location", "Unknown Location")

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    # Check today's attendance
    cur.execute("""
        SELECT attendance_id
        FROM attendance
        WHERE member_id=?
        AND attendance_date=date('now')
    """, (member_id,))

    today = cur.fetchone()

    if today:

        flash("Today's attendance is already marked.", "warning")

    else:

        cur.execute("""
            INSERT INTO attendance(
                member_id,
                attendance_date,
                check_in_time,
                latitude,
                longitude,
                location,
                status
            )
            VALUES(
                ?,
                date('now'),
                time('now','localtime'),
                ?,
                ?,
                ?,
                'Present'
            )
        """, (
            member_id,
            lat,
            lng,
            location
        ))

        conn.commit()

        flash("Attendance marked successfully.", "success")

    conn.close()

    return redirect(url_for('member_attendance'))

@app.route('/member_profile')
@member_required
def member_profile():

    if 'member_id' not in session:
        return redirect(url_for('member_login'))

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM members
        WHERE member_id=?
    """, (session['member_id'],))

    member = cur.fetchone()

    conn.close()

    return render_template(
        "member_profile.html",
        member=member
    )

@app.route('/member_update_profile', methods=['GET', 'POST'])
@member_required
def member_update_profile():

    if 'member_id' not in session:
        return redirect(url_for('member_login'))

    member_id = session['member_id']

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    if request.method == 'POST':

        mobile = request.form['mobile'].strip()
        email = request.form['email'].strip()
        height = request.form['height']
        weight = request.form['weight']
        address = request.form['address'].strip()

        # Mobile Validation
        if not mobile.isdigit() or len(mobile) != 10:
            flash("Mobile number must be exactly 10 digits.", "warning")
            return redirect(url_for('member_update_profile'))

        # Email Validation
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

        if email and not re.match(email_pattern, email):
            flash("Enter a valid email address.", "warning")
            return redirect(url_for('member_update_profile'))

        # Duplicate Mobile
        cur.execute("""
            SELECT *
            FROM members
            WHERE mobile=?
            AND member_id!=?
        """, (mobile, member_id))

        if cur.fetchone():
            flash("Mobile number already exists.", "warning")
            conn.close()
            return redirect(url_for('member_update_profile'))

        # Duplicate Email
        cur.execute("""
            SELECT *
            FROM members
            WHERE email=?
            AND member_id!=?
        """, (email, member_id))

        if cur.fetchone():
            flash("Email already exists.", "warning")
            conn.close()
            return redirect(url_for('member_update_profile'))

        # Update Profile
        cur.execute("""
            UPDATE members
            SET
                mobile=?,
                email=?,
                height=?,
                weight=?,
                address=?
            WHERE member_id=?
        """, (
            mobile,
            email,
            height,
            weight,
            address,
            member_id
        ))

        conn.commit()

        flash("Profile Updated Successfully.", "success")

        conn.close()

        return redirect(url_for('member_profile'))

    cur.execute("""
        SELECT *
        FROM members
        WHERE member_id=?
    """, (member_id,))

    member = cur.fetchone()

    conn.close()

    return render_template(
        "member_update_profile.html",
        member=member
    )

@app.route('/change_password', methods=['GET', 'POST'])
@member_required
def change_password():

    if 'member_id' not in session:
        return redirect(url_for('member_login'))

    member_id = session['member_id']

    conn = get_connection()
    conn.row_factory = sql.Row
    cur = conn.cursor()

    if request.method == 'POST':

        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        cur.execute("""
            SELECT password
            FROM members
            WHERE member_id=?
        """, (member_id,))

        member = cur.fetchone()

        if member['password'] != current_password:

            flash("Current Password is incorrect.", "danger")

            conn.close()

            return redirect(url_for('change_password'))

        if len(new_password) < 8:

            flash("New Password must be at least 8 characters.", "warning")

            conn.close()

            return redirect(url_for('change_password'))

        if new_password != confirm_password:

            flash("Confirm Password does not match.", "warning")

            conn.close()

            return redirect(url_for('change_password'))

        cur.execute("""
            UPDATE members
            SET password=?
            WHERE member_id=?
        """, (new_password, member_id))

        conn.commit()
        conn.close()

        flash("Password Changed Successfully.", "success")

        return redirect(url_for('member_profile'))

    conn.close()

    return render_template("change_password.html")

if __name__ == '__main__':
    app.run(debug=True)


