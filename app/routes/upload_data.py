from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models import db, Data, DataType, Studylog, SharedData
from app.forms import (StudySessionForm, AssessmentResultForm, VocabularyForm,
                       LearningGoalForm, BulkUploadForm)
from datetime import datetime, timedelta
import json
import os

upload_data_bp = Blueprint('upload_data_bp', __name__, url_prefix='/data')


@upload_data_bp.route('/upload')
@upload_data_bp.route('/upload/<upload_type>')
@login_required
def upload(upload_type=None):
    """Main upload page with different data types"""
    # Get recent uploads for sidebar
    recent_uploads = get_recent_uploads(current_user.id)

    # Initialize forms
    form = None
    if upload_type == 'study_session':
        form = StudySessionForm()
    elif upload_type == 'assessment':
        form = AssessmentResultForm()
    elif upload_type == 'vocabulary':
        form = VocabularyForm()
    elif upload_type == 'goals':
        form = LearningGoalForm()

    # Always initialize bulk_form since it's used in the template
    bulk_form = BulkUploadForm()

    return render_template('upload_data.html',
                           upload_type=upload_type,
                           form=form,
                           bulk_form=bulk_form,
                           recent_uploads=recent_uploads)

@upload_data_bp.route('/upload/study_session', methods=['POST'])
@login_required
def upload_study_session():
    """Handle study session upload"""
    form = StudySessionForm()

    if form.validate_on_submit():
        # Create study log
        studylog = Studylog(
            user_id=current_user.id,
            date=form.date.data.strftime('%Y-%m-%d'),
            duration_minutes=form.duration_minutes.data,
            activity_type=form.activity_type.data,
            skills=','.join(form.get_selected_skills()),
            notes=form.notes.data,
            rating=form.rating.data
        )

        # Create data record
        data = Data(
            user_id=current_user.id,
            title=f"Study Session - {form.date.data.strftime('%Y-%m-%d')}",
            data_type=DataType.STUDY_TIME,
            description=form.notes.data,
            content=json.dumps({
                'date': form.date.data.strftime('%Y-%m-%d'),
                'duration_minutes': form.duration_minutes.data,
                'activity_type': form.activity_type.data,
                'skills': form.get_selected_skills(),
                'rating': form.rating.data
            })
        )

        db.session.add(studylog)
        db.session.add(data)
        db.session.commit()

        flash('Study session logged successfully!', 'success')
        return redirect(url_for('upload_data_bp.my_data'))

    # If validation fails, return to form with errors
    return redirect(url_for('upload_data_bp.upload', upload_type='study_session'))


@upload_data_bp.route('/upload/assessment', methods=['POST'])
@login_required
def upload_assessment():
    """Handle assessment upload"""
    form = AssessmentResultForm()

    if form.validate_on_submit():
        # Create data record
        data = Data(
            user_id=current_user.id,
            title=f"{form.assessment_name.data} - {form.date_taken.data.strftime('%Y-%m-%d')}",
            data_type=DataType.ASSESSMENT,
            description=form.feedback.data,
            content=json.dumps({
                'assessment_name': form.assessment_name.data,
                'assessment_type': form.assessment_type.data,
                'date_taken': form.date_taken.data.strftime('%Y-%m-%d'),
                'score': form.score.data,
                'max_score': form.max_score.data,
                'percentage': round(form.score.data / form.max_score.data * 100, 2),
                'skill_area': form.skill_area.data,
                'feedback': form.feedback.data
            })
        )

        db.session.add(data)
        db.session.commit()

        flash('Assessment results added successfully!', 'success')
        return redirect(url_for('upload_data_bp.my_data'))

    # If validation fails, return to form with errors
    return redirect(url_for('upload_data_bp.upload', upload_type='assessment'))


@upload_data_bp.route('/upload/vocabulary', methods=['POST'])
@login_required
def upload_vocabulary():
    """Handle vocabulary upload"""
    form = VocabularyForm()

    if form.validate_on_submit():
        # Create data record
        data = Data(
            user_id=current_user.id,
            title=f"Vocabulary: {form.word.data}",
            data_type=DataType.VOCABULARY,
            description=form.definition.data,
            content=json.dumps({
                'word': form.word.data,
                'translation': form.translation.data,
                'definition': form.definition.data,
                'context': form.context.data,
                'category': form.category.data,
                'level': form.level.data
            })
        )

        db.session.add(data)
        db.session.commit()

        flash('Vocabulary added successfully!', 'success')
        return redirect(url_for('upload_data_bp.upload', upload_type='vocabulary'))

    # If validation fails, return to form with errors
    return redirect(url_for('upload_data_bp.upload', upload_type='vocabulary'))


@upload_data_bp.route('/upload/bulk', methods=['POST'])
@login_required
def bulk_upload():
    """Handle bulk file upload"""
    form = BulkUploadForm()

    if form.validate_on_submit():
        file = form.file.data
        if file:
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"

            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id))
            os.makedirs(upload_dir, exist_ok=True)

            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)

            # Create data record
            data = Data(
                user_id=current_user.id,
                title=f"Bulk Upload: {file.filename}",
                data_type=DataType.OTHER,
                description=f"Uploaded file: {file.filename}",
                file_path=filepath,
                extra_metadata={
                    'original_filename': file.filename,
                    'file_size': os.path.getsize(filepath),
                    'overwrite': form.overwrite.data
                }
            )

            db.session.add(data)
            db.session.commit()

            flash('File uploaded successfully! Processing will begin shortly.', 'success')
            return redirect(url_for('upload_data_bp.my_data'))

    flash('Error uploading file. Please try again.', 'error')
    return redirect(url_for('upload_data_bp.upload'))


@upload_data_bp.route('/my_data')
@login_required
def my_data():
    """Display user's uploaded data"""
    # Get all user's data
    user_data = Data.query.filter_by(user_id=current_user.id).order_by(Data.created_at.desc()).all()

    # Get data shared with user
    shared_data = db.session.query(Data).join(SharedData, Data.id == SharedData.data_id) \
        .filter(SharedData.recipient_id == current_user.id).all()

    return render_template('my_data.html', user_data=user_data, shared_data=shared_data)


@upload_data_bp.route('/view/<int:id>')
@login_required
def view(id):
    """View specific data entry"""
    data = Data.query.get_or_404(id)

    # Check if user has access
    if data.user_id != current_user.id:
        # Check if data is shared with user
        shared = SharedData.query.filter_by(data_id=id, recipient_id=current_user.id).first()
        if not shared:
            flash('You do not have permission to view this data.', 'error')
            return redirect(url_for('upload_data_bp.my_data'))

    return render_template('view_data.html', data=data)


@upload_data_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete a data entry"""
    data = Data.query.get_or_404(id)

    # Check if user owns the data
    if data.user_id != current_user.id:
        flash('You do not have permission to delete this data.', 'error')
        return redirect(url_for('upload_data_bp.my_data'))

    # Delete associated file if exists
    if data.file_path and os.path.exists(data.file_path):
        try:
            os.remove(data.file_path)
        except OSError:
            pass  # File might not exist

    db.session.delete(data)
    db.session.commit()

    flash('Data deleted successfully.', 'success')
    return redirect(url_for('upload_data_bp.my_data'))


def get_recent_uploads(user_id, limit=5):
    """Get recent uploads for the sidebar"""
    recent_data = Data.query.filter_by(user_id=user_id) \
        .order_by(Data.created_at.desc()) \
        .limit(limit).all()

    # Add days ago calculation
    for data in recent_data:
        days_diff = (datetime.now() - data.created_at).days
        data.days_ago = days_diff

    return recent_data


def secure_filename(filename):
    """Make filename safe for filesystem"""
    import re
    # Remove non-alphanumeric characters except dots and underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    return filename