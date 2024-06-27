from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Opportunity
from . import db, views
import json



views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    data = Opportunity.query.all()
    return render_template("home.html", user=current_user, data=data)



@views.route('/create-opportunity', methods=['GET', 'POST'])
@login_required
def create_opportunity():
    if not current_user.is_admin:
        flash('You do not have permission to create an opportunity.', category='error')
        return redirect(url_for('views.home'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        data = request.form.get('body')
        if len(data) < 1 or len(title) < 1:
            flash('Missing information.', category='error')
        else:
            new_opportunity = Opportunity(title=title, data=data, employee_id=current_user.id)
            db.session.add(new_opportunity)
            db.session.commit()
            flash('Opportunity created!', category='success')
            return redirect(url_for('views.home'))
    return render_template("views.create_opportunity.html")


@views.route('/view-opportunity/<int:opportunity_id>', methods=['GET'])
@login_required
def view_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    return render_template("view_opportunity.html", opportunity=opportunity)


@views.route('/request-join/<int:opportunity_id>', methods=['POST'])
@login_required
def request_join(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    if current_user.role == 'admin':
        # Admin-specific logic here
        pass
    else:
        # Logic for normal users to notify the admin
        flash('Admin has been notified.', category='info')
    return redirect(url_for('views.home', opportunity_id=opportunity_id))


@views.route('/edit-opportunity/<int:opportunity_id>', methods=['GET', 'POST'])
@login_required
def edit_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    if current_user.role != 'admin':
        flash('You do not have permission to edit this opportunity.', category='error')
        return redirect(url_for('views.home'))
    
    if request.method == 'POST':
        new_data = request.form.get('data')
        if len(new_data) < 1:
            flash('Opportunity is too short!', category='error')
        else:
            opportunity.data = new_data
            db.session.commit()
            flash('Opportunity updated!', category='success')
            return redirect(url_for('views.home'))
    return render_template("edit_opportunity.html", user=current_user, opportunity=opportunity)



@views.route('/delete-opportunity/<int:opportunity_id>', methods=['GET', 'POST'])
@login_required
def delete_opportunity(opportunity_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    opportunity = Opportunity.query.get(opportunity_id)
    if opportunity:
        db.session.delete(opportunity)
        db.session.commit()
        flash('Opportunity deleted!', category='success')
    else:
        flash('Opportunity not found.', category='error')

    return redirect(url_for('views.home'))
