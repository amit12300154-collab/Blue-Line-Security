from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database import db
from models.emergency_contact import EmergencyContact
from utils.validators import validate_email, validate_phone

contacts_bp = Blueprint('contacts', __name__, url_prefix='/contacts')


@contacts_bp.route('/', methods=['GET'])
@login_required
def list_contacts():
    """List all emergency contacts registered by the current user."""
    contacts = (
        EmergencyContact.query
        .filter_by(user_id=current_user.id)
        .order_by(EmergencyContact.priority.asc(), EmergencyContact.created_at.asc())
        .all()
    )
    return render_template('contacts.html', contacts=contacts)


@contacts_bp.route('/add', methods=['POST'])
@login_required
def add_contact():
    """Add a new emergency contact."""
    name = request.form.get('name', '').strip()
    relationship = request.form.get('relationship', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    priority = request.form.get('priority', 1)

    errors = []
    if not name:
        errors.append("Contact name is required.")
    if not relationship:
        errors.append("Relationship is required.")
    if not phone or not validate_phone(phone):
        errors.append("A valid phone number is required.")
    if email and not validate_email(email):
        errors.append("If provided, email must be a valid format.")

    try:
        priority = int(priority)
    except (ValueError, TypeError):
        priority = 1

    if errors:
        for err in errors:
            flash(err, 'danger')
        return redirect(url_for('contacts.list_contacts'))

    new_contact = EmergencyContact(
        user_id=current_user.id,
        name=name,
        relationship=relationship,
        phone=phone,
        email=email if email else None,
        priority=priority,
        is_active=True
    )

    try:
        db.session.add(new_contact)
        db.session.commit()
        flash(f"Emergency contact '{name}' added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Failed to add emergency contact. Please try again.", "danger")

    return redirect(url_for('contacts.list_contacts'))


@contacts_bp.route('/edit/<int:contact_id>', methods=['POST'])
@login_required
def edit_contact(contact_id: int):
    """Update details of an existing emergency contact."""
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=current_user.id).first()
    if not contact:
        flash("Contact not found or unauthorized access.", "danger")
        return redirect(url_for('contacts.list_contacts'))

    name = request.form.get('name', '').strip()
    relationship = request.form.get('relationship', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    priority = request.form.get('priority', 1)

    if not name or not relationship or not validate_phone(phone):
        flash("Please provide a valid name, relationship, and phone number.", "danger")
        return redirect(url_for('contacts.list_contacts'))

    if email and not validate_email(email):
        flash("Invalid email format.", "danger")
        return redirect(url_for('contacts.list_contacts'))

    try:
        priority = int(priority)
    except (ValueError, TypeError):
        priority = 1

    contact.name = name
    contact.relationship = relationship
    contact.phone = phone
    contact.email = email if email else None
    contact.priority = priority

    db.session.commit()
    flash(f"Emergency contact '{name}' updated successfully.", "success")
    return redirect(url_for('contacts.list_contacts'))


@contacts_bp.route('/delete/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id: int):
    """Delete an emergency contact."""
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=current_user.id).first()
    if not contact:
        flash("Contact not found or unauthorized access.", "danger")
        return redirect(url_for('contacts.list_contacts'))

    name = contact.name
    db.session.delete(contact)
    db.session.commit()
    flash(f"Contact '{name}' was removed from your emergency list.", "info")
    return redirect(url_for('contacts.list_contacts'))


@contacts_bp.route('/toggle/<int:contact_id>', methods=['POST'])
@login_required
def toggle_contact(contact_id: int):
    """Toggle contact active/inactive status."""
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=current_user.id).first()
    if not contact:
        flash("Contact not found.", "danger")
        return redirect(url_for('contacts.list_contacts'))

    contact.is_active = not contact.is_active
    db.session.commit()
    status_text = "activated" if contact.is_active else "deactivated"
    flash(f"Contact '{contact.name}' {status_text}.", "info")
    return redirect(url_for('contacts.list_contacts'))
