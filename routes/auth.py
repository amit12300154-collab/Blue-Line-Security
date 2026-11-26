from urllib.parse import urlparse
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from database import db
from models.user import User
from utils.validators import validate_email, validate_phone

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration view."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.user_dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        address = request.form.get('address', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        terms = request.form.get('terms')

        # Validations
        errors = []
        if not full_name:
            errors.append("Full Name is required.")
        if not email or not validate_email(email):
            errors.append("A valid email address is required.")
        if not phone or not validate_phone(phone):
            errors.append("A valid phone number (at least 7 digits) is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if not terms:
            errors.append("You must agree to the Terms of Service & Privacy Policy.")

        # Check existing user
        if not errors:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                errors.append("An account with this email already exists. Please log in.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'register.html',
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                blood_group=blood_group
            )

        # Create user
        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address if address else None,
            blood_group=blood_group if blood_group else None,
            role="USER",
            is_active=True
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "danger")

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User and Administrator login view."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('dashboard.user_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password. Please verify your credentials.", "danger")
            return render_template('login.html', email=email)

        if not user.is_active:
            flash("Your account has been deactivated. Please contact support.", "warning")
            return render_template('login.html', email=email)

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.full_name}!", "success")

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/') and not next_page.startswith('//') \
                and not urlparse(next_page).netloc and '\\' not in next_page:
            return redirect(next_page)

        if user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('dashboard.user_dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Sign out user and clear session."""
    logout_user()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and update profile information."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        new_password = request.form.get('new_password', '')

        if not full_name:
            flash("Full name cannot be empty.", "danger")
            return render_template('profile.html', user=current_user)

        if not validate_phone(phone):
            flash("Please enter a valid phone number.", "danger")
            return render_template('profile.html', user=current_user)

        current_user.full_name = full_name
        current_user.phone = phone
        current_user.address = address if address else None
        current_user.blood_group = blood_group if blood_group else None

        if new_password:
            if len(new_password) < 6:
                flash("New password must be at least 6 characters.", "danger")
                return render_template('profile.html', user=current_user)
            current_user.set_password(new_password)
            flash("Password updated successfully.", "info")

        db.session.commit()
        flash("Profile updated successfully.", "success")

    return render_template('profile.html', user=current_user)
