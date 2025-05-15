#app/routes/api.py
import logging
from datetime import datetime, timedelta, timezone
import json
from app.extensions import db
from flask import Blueprint, jsonify, request, url_for, Flask, flash, redirect
from flask_login import login_required, current_user
from flask_socketio import emit
from sqlalchemy import or_
from sqlalchemy.orm import Session


from app.models import (
    Data,
    SharedData,
    Sharegroup,
    Sharegroupmember,
    SharedPermission,
    DataType,
    User,
    Progress,  # Assuming these are in models.py
    Studylog,
)
from app import socketio  # Import socketio
from app.forms import StudySessionForm #Import the form

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")


def get_shared_data_types(owner_id: int, recipient_id: int, db_session: Session):
    """Helper function to get shared data types between two users."""
    return (
        db_session.query(Data.data_type)
        .join(SharedData, SharedData.data_id == Data.id)
        .filter(
            SharedData.owner_id == owner_id, SharedData.recipient_id == recipient_id
        )
        .distinct()
        .all()
    )


@api_bp.route("/shared_users")
@login_required
def get_shared_users():
    """Get users with whom data is shared."""
    try:
        shared_users_data = (
            db.session.query(User, SharedData)
            .join(SharedData, SharedData.recipient_id == User.id)
            .filter(SharedData.owner_id == current_user.id)
            .distinct(User.id)
            .all()
        )

        users = []
        for user, shared_data in shared_users_data:
            shared_types = get_shared_data_types(
                current_user.id, user.id, db.session
            )
            users.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "permission": shared_data.permission.value,
                    "shared_data": [
                        {
                            "type": data_type[0].value,
                            "label": data_type[0].value.replace("_", " ").title(),
                            "shared": True,
                        }
                        for data_type in shared_types
                    ],
                }
            )
        return jsonify({"users": users})
    except Exception as e:
        logger.error(f"Error in get_shared_users: {e}")
        return jsonify({"error": "Failed to retrieve shared users"}), 500



@api_bp.route("/share_groups")
@login_required
def get_share_groups():
    """Get user's share groups."""
    try:
        # Groups owned by user
        owned_groups = Sharegroup.query.filter_by(owner_id=current_user.id).all()

        # Groups user is member of
        member_groups = (
            db.session.query(Sharegroup)
            .join(Sharegroupmember, Sharegroupmember.group_id == Sharegroup.id)
            .filter(Sharegroupmember.user_id == current_user.id)
            .all()
        )

        all_groups = list(set(owned_groups + member_groups))

        groups = []
        for group in all_groups:
            member_count = Sharegroupmember.query.filter_by(
                group_id=group.id
            ).count()

            groups.append(
                {
                    "id": group.id,
                    "name": group.name,
                    "description": "",  # Add description field to Sharegroup model if needed
                    "member_count": member_count,
                    "is_owner": group.owner_id == current_user.id,
                    "shared_data": [
                        {
                            "type": "vocabulary",
                            "label": "Vocabulary",
                            "shared": True,
                        },
                        {
                            "type": "study_time",
                            "label": "Study Time",
                            "shared": True,
                        },
                    ],
                }
            )

        return jsonify({"groups": groups})
    except Exception as e:
        logger.error(f"Error in get_share_groups: {e}")
        return jsonify({"error": "Failed to retrieve share groups"}), 500


@api_bp.route("/shared_with_me")
@login_required
def get_shared_with_me():
    """Get data shared with current user."""
    try:
        shared_data_items = (
            db.session.query(Data, SharedData, User)
            .join(SharedData, SharedData.data_id == Data.id)
            .join(User, User.id == SharedData.owner_id)
            .filter(SharedData.recipient_id == current_user.id)
            .all()
        )

        data_list = []
        for data, shared, owner in shared_data_items:
            data_list.append(
                {
                    "id": data.id,
                    "title": data.title,
                    "data_type": data.data_type.value,
                    "owner_name": owner.name,
                    "created_at": shared.created_at.isoformat(),
                    "permission": shared.permission.value,
                    "view_url": url_for("data_bp.view", id=data.id),
                }
            )
        return jsonify({"shared_data": data_list})
    except Exception as e:
        logger.error(f"Error in get_shared_with_me: {e}")
        return jsonify({"error": "Failed to retrieve data shared with you"}), 500



@api_bp.route("/share_history")
@login_required
def get_share_history():
    """Get sharing history."""
    try:
        history_items_data = (
            db.session.query(SharedData, Data, User)
            .join(Data, SharedData.data_id == Data.id)
            .join(User, User.id == SharedData.recipient_id)
            .filter(SharedData.owner_id == current_user.id)
            .order_by(SharedData.created_at.desc())
            .limit(20)
            .all()
        )

        history_items = []
        for shared, data, recipient in history_items_data:
            history_items.append(
                {
                    "id": shared.id,
                    "title": f"Shared {data.title} with {recipient.name}",
                    "description": f"You shared {data.data_type.value.replace('_', ' ')} data",
                    "created_at": shared.created_at.isoformat(),
                    "permission": shared.permission.value,
                }
            )
        return jsonify({"history": history_items})
    except Exception as e:
        logger.error(f"Error in get_share_history: {e}")
        return jsonify({"error": "Failed to retrieve share history"}), 500


@api_bp.route("/quick_share_groups")
@login_required
def get_quick_share_groups():
    """Get quick share groups."""
    try:
        groups = Sharegroup.query.filter_by(owner_id=current_user.id).limit(3).all()

        group_list = [{"id": group.id, "name": group.name} for group in groups]
        return jsonify({"groups": group_list})
    except Exception as e:
        logger.error(f"Error in get_quick_share_groups: {e}")
        return jsonify({"error": "Failed to retrieve quick share groups"}), 500



@api_bp.route("/my_data_summary")
@login_required
def get_my_data_summary():
    """Get user's data for sharing."""
    try:
        user_data = (
            Data.query.filter_by(user_id=current_user.id)
            .order_by(Data.created_at.desc())
            .all()
        )

        data_items = [
            {"id": data.id, "title": data.title, "data_type": data.data_type.value, "description": data.description}
            for data in user_data
        ]
        return jsonify({"data_items": data_items})
    except Exception as e:
        logger.error(f"Error in get_my_data_summary: {e}")
        return jsonify({"error": "Failed to retrieve your data summary"}), 500



@api_bp.route("/search_users")
@login_required
def search_users():
    """Search users for sharing."""
    query = request.args.get("q", "").strip()

    if len(query) < 2:
        return jsonify({"users": []})

    try:
        users = (
            User.query.filter(
                User.id != current_user.id,
                or_(
                    User.name.ilike(f"%{query}%"), User.email.ilike(f"%{query}%")
                ),
            )
            .limit(10)
            .all()
        )

        user_list = [{"id": user.id, "name": user.name, "email": user.email} for user in users]
        return jsonify({"users": user_list})
    except Exception as e:
        logger.error(f"Error in search_users: {e}")
        return jsonify({"error": "Failed to search users"}), 500



@api_bp.route("/share_data", methods=["POST"])
@login_required
def share_data():
    """Share data with users."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    recipient_id = data.get("recipient_id")
    recipient_email = data.get("recipient_email")
    data_ids = data.get("data_ids", [])
    permission = data.get("permission", "read")
    message = data.get("message", "")  # Not used, consider adding to model

    if not data_ids:
        return jsonify({"error": "No data selected for sharing"}), 400

    if not recipient_id and recipient_email:
        recipient = User.query.filter_by(email=recipient_email).first()
        if not recipient:
            return jsonify({"error": "User not found"}), 404
        recipient_id = recipient.id

    if not recipient_id:
        return jsonify({"error": "Recipient not specified"}), 400

    try:
        for data_id in data_ids:
            data_item = Data.query.filter_by(
                id=data_id, user_id=current_user.id
            ).first()
            if not data_item:
                logger.warning(
                    f"Data with id {data_id} not found or does not belong to user {current_user.id}"
                )
                continue  # Skip to the next data_id

            existing = SharedData.query.filter_by(
                data_id=data_id,
                owner_id=current_user.id,
                recipient_id=recipient_id,
            ).first()

            if existing:
                existing.permission = SharedPermission[permission.upper()]
            else:
                shared_data = SharedData(
                    data_id=data_id,
                    owner_id=current_user.id,
                    recipient_id=recipient_id,
                    permission=SharedPermission[permission.upper()],
                )
                db.session.add(shared_data)

        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in share_data: {e}")
        return jsonify({"error": "Failed to share data"}), 500



@api_bp.route("/create_group", methods=["POST"])
@login_required
def create_group():
    """Create a new share group."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Group name is required"}), 400

    try:
        existing = Sharegroup.query.filter_by(
            owner_id=current_user.id, name=name
        ).first()
        if existing:
            return jsonify({"error": "Group with this name already exists"}), 400

        group = Sharegroup(owner_id=current_user.id, name=name)
        db.session.add(group)
        db.session.flush()  # Get the new group's ID

        member = Sharegroupmember(group_id=group.id, user_id=current_user.id)
        db.session.add(member)
        db.session.commit()

        return jsonify({"success": True, "group_id": group.id})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in create_group: {e}")
        return jsonify({"error": "Failed to create group"}), 500



@api_bp.route("/update_sharing/<int:user_id>", methods=["PUT"])
@login_required
def update_sharing(user_id):
    """Update sharing settings with a user."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    permission = data.get("permission", "read")

    try:
        shared_data_items = SharedData.query.filter_by(
            owner_id=current_user.id, recipient_id=user_id
        ).all()

        for item in shared_data_items:
            item.permission = SharedPermission[permission.upper()]

        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in update_sharing: {e}")
        return jsonify({"error": "Failed to update sharing settings"}), 500



@api_bp.route("/revoke_share/<int:user_id>", methods=["DELETE"])
@login_required
def revoke_share(user_id):
    """Revoke all sharing with a user."""
    try:
        SharedData.query.filter_by(
            owner_id=current_user.id, recipient_id=user_id
        ).delete()
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in revoke_share: {e}")
        return jsonify({"error": "Failed to revoke sharing"}), 500



@api_bp.route("/update_group_sharing/<int:group_id>", methods=["PUT"])
@login_required
def update_group_sharing(group_id):
    """Update group sharing settings."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # shared_types = data.get("shared_data", []) # Not used
    try:
        #  Add logic to update group-wide sharing settings
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error in update_group_sharing: {e}")
        return jsonify({"error": "Failed to update group sharing settings"}), 500



@api_bp.route("/leave_group/<int:group_id>", methods=["DELETE"])
@login_required
def leave_group(group_id):
    """Leave or delete a group."""
    try:
        group = Sharegroup.query.get_or_404(group_id)  # Raises 404 if not found

        if group.owner_id == current_user.id:
            Sharegroupmember.query.filter_by(group_id=group_id).delete()
            db.session.delete(group)
        else:
            Sharegroupmember.query.filter_by(
                group_id=group_id, user_id=current_user.id
            ).delete()

        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in leave_group: {e}")
        return jsonify({"error": "Failed to leave/delete group"}), 500



@api_bp.route("/group_members/<int:group_id>")
@login_required
def get_group_members(group_id):
    """Get group members."""
    try:
        members_data = (
            db.session.query(User, Sharegroupmember)
            .join(Sharegroupmember, Sharegroupmember.user_id == User.id)
            .filter(Sharegroupmember.group_id == group_id)
            .all()
        )

        group = Sharegroup.query.get_or_404(group_id)

        member_list = [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_owner": user.id == group.owner_id,
            }
            for user, membership in members_data
        ]
        return jsonify({"members": member_list})
    except Exception as e:
        logger.error(f"Error in get_group_members: {e}")
        return jsonify({"error": "Failed to retrieve group members"}), 500



@api_bp.route("/share_details/<int:share_id>")
@login_required
def get_share_details(share_id):
    """Get details of a specific share."""
    try:
        shared_data = (
            db.session.query(SharedData, Data, User)
            .join(Data, SharedData.data_id == Data.id)
            .join(User, User.id == SharedData.recipient_id)
            .filter(SharedData.id == share_id, SharedData.owner_id == current_user.id)
            .first()
        )

        if not shared_data:
            return jsonify({"error": "Share not found"}), 404

        shared, data, recipient = shared_data

        return jsonify(
            {
                "id": shared.id,
                "recipient_name": recipient.name,
                "data_type": data.data_type.value,
                "permission": shared.permission.value,
                "created_at": shared.created_at.isoformat(),
                "message": "",  # Add message field to SharedData model if needed
            }
        )
    except Exception as e:
        logger.error(f"Error in get_share_details: {e}")
        return jsonify({"error": "Failed to retrieve share details"}), 500



@api_bp.route("/search_shared_users")
@login_required
def search_shared_users():
    """Search among users with whom data is shared."""
    query = request.args.get("q", "").strip()

    users_query = (
        db.session.query(User, SharedData)
        .join(SharedData, SharedData.recipient_id == User.id)
        .filter(SharedData.owner_id == current_user.id)
    )

    if query:
        users_query = users_query.filter(
            or_(
                User.name.ilike(f"%{query}%"), User.email.ilike(f"%{query}%")
            )
        )

    try:
        shared_users = users_query.distinct(User.id).all()

        users = []
        for user, shared_data in shared_users:
            shared_types = get_shared_data_types(
                current_user.id, user.id, db.session
            )
            users.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "permission": shared_data.permission.value,
                    "shared_data": [
                        {
                            "type": data_type[0].value,
                            "label": data_type[0].value.replace("_", " ").title(),
                            "shared": True,
                        }
                        for data_type in shared_types
                    ],
                }
            )
        return jsonify({"users": users})
    except Exception as e:
        logger.error(f"Error in search_shared_users: {e}")
        return jsonify({"error": "Failed to search shared users"}), 500



@api_bp.route("/search_groups")
@login_required
def search_groups():
    """Search user's share groups."""
    query = request.args.get("q", "").strip()

    groups_query = db.session.query(Sharegroup).filter(
        or_(
            Sharegroup.owner_id == current_user.id,
            Sharegroup.id.in_(
                db.session.query(Sharegroupmember.group_id).filter(
                    Sharegroupmember.user_id == current_user.id
                )
            ),
        )
    )

    if query:
        groups_query = groups_query.filter(Sharegroup.name.ilike(f"%{query}%"))

    try:
        groups = groups_query.all()

        group_list = []
        for group in groups:
            member_count = Sharegroupmember.query.filter_by(
                group_id=group.id
            ).count()

            group_list.append(
                {
                    "id": group.id,
                    "name": group.name,
                    "description": "",
                    "member_count": member_count,
                    "is_owner": group.owner_id == current_user.id,
                    "shared_data": [
                        {
                            "type": "vocabulary",
                            "label": "Vocabulary",
                            "shared": True,
                        },
                        {
                            "type": "study_time",
                            "label": "Study Time",
                            "shared": True,
                        },
                    ],
                }
            )
        return jsonify({"groups": group_list})
    except Exception as e:
        logger.error(f"Error in search_groups: {e}")
        return jsonify({"error": "Failed to search groups"}), 500



@api_bp.route('/visualization_data')
@login_required
def visualization_data():
    """Get data for visualization"""
    days = request.args.get('days', default=7, type=int)
    user_id = current_user.id

    # Get the current user's progress and study log data
    progress_data = Progress.query.filter_by(user_id=user_id).order_by(Progress.date.desc()).limit(days).all()
    studylog_data = Studylog.query.filter_by(user_id=user_id).order_by(Studylog.date.desc()).limit(days).all()

    
    skill_trends = []
    distribution_data = {}
    radar_data = {}
    vocab_data = []
    insights = {}


    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    # Progress data (skills and vocabulary)
    progress_data = Progress.query.filter(
        Progress.user_id == current_user.id,
        Progress.date >= start_date.strftime('%Y-%m-%d'),
        Progress.date <= end_date.strftime('%Y-%m-%d')
    ).order_by(Progress.date).all()

    # Aggregate skill scores
    skill_trends = []
    for p in progress_data:
        skill_trends.append({
            'date': p.date,
            'listening': p.listening or 0,
            'reading': p.reading or 0,
            'speaking': p.speaking or 0,
            'writing': p.writing or 0,
            'vocabulary_count': p.vocabulary_count or 0
        })

    # Latest skill scores for radar chart
    latest_progress = Progress.query.filter(
        Progress.user_id == current_user.id
    ).order_by(Progress.date.desc()).first()

    radar_data = {
        'listening': latest_progress.listening if latest_progress else 0,
        'reading': latest_progress.reading if latest_progress else 0,
        'speaking': latest_progress.speaking if latest_progress else 0,
        'writing': latest_progress.writing if latest_progress else 0,
        'vocabulary': latest_progress.vocabulary_count if latest_progress else 0
    }

    # Study time distribution
    study_logs = Studylog.query.filter(
        Studylog.user_id == current_user.id,
        Studylog.date >= start_date.strftime('%Y-%m-%d'),
        Studylog.date <= end_date.strftime('%Y-%m-%d')
    ).all()

    skill_distribution = {
        'reading': 0,
        'writing': 0,
        'listening': 0,
        'speaking': 0,
        'grammar': 0
    }
    total_minutes = 0
    for log in study_logs:
        skills = log.skills.split(',') if log.skills else []
        minutes = log.duration_minutes or 0
        total_minutes += minutes
        for skill in skills:
            if skill in skill_distribution:
                skill_distribution[skill] += minutes

    # Convert to hours and percentages
    distribution_data = {}
    total_hours = total_minutes / 60
    for skill, minutes in skill_distribution.items():
        hours = minutes / 60
        percentage = (minutes / total_minutes * 100) if total_minutes > 0 else 0
        distribution_data[skill] = {
            'hours': round(hours, 1),
            'percentage': round(percentage, 1)
        }

    # Vocabulary growth (assuming active/passive split is estimated)
    vocab_data = []
    active_vocab = 0
    passive_vocab = 0
    for p in progress_data:
        vocab_count = p.vocabulary_count or 0
        active_vocab += vocab_count // 2  # Example: 50% active
        passive_vocab += vocab_count // 2  # Example: 50% passive
        vocab_data.append({
            'date': p.date,
            'active': active_vocab,
            'passive': passive_vocab
        })

    # Insights
    insights = {
        'growth': '+0%',
        'most_improved': 'Listening',
        'least_improved': 'Speaking',
        'current_level': latest_progress.level if latest_progress else 'Unknown',
        'strongest_score': max(radar_data.values()) if radar_data else 0,
        'weakest_score': min(radar_data.values()) if radar_data else 0,
        'listening_growth': '+10%',
        'active_vocab': active_vocab,
        'active_vocab_growth': '+52',
        'passive_vocab': passive_vocab,
        'passive_vocab_growth': '+107',
        'vocab_level': 'B1+'
    }

    # Calculate actual growth rate
    if skill_trends:
        first = skill_trends[0]
        last = skill_trends[-1]
        avg_first = (first['listening'] + first['reading'] + first['speaking'] + first['writing']) / 4
        avg_last = (last['listening'] + last['reading'] + last['speaking'] + last['writing']) / 4
        growth = f'+{round((avg_last - avg_first) / avg_first * 100, 1)}%' if avg_first > 0 else '+0%'
        insights['growth'] = growth

    return jsonify({
        'skill_trends': skill_trends,
        'radar_data': radar_data,
        'distribution_data': distribution_data,
        'vocab_data': vocab_data,
        'insights': insights
    })

@api_bp.route('/upload/study_session', methods=['POST'])
@login_required
def upload_study_session():
    """Handle study session upload"""
    form = StudySessionForm()

    if form.validate_on_submit():
        try:
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

            socketio.emit('new_data', {'user_id': current_user.id})  # 新增 WebSocket 推送

            flash('Study session logged successfully!', 'success')
            return redirect(url_for('data_bp.my_data'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in upload_study_session: {e}")
            flash('Failed to log study session.', 'error')
            return redirect(url_for('data_bp.upload', upload_type='study_session'))

    # If validation fails, return to form with errors
    return redirect(url_for('data_bp.upload', upload_type='study_session'))
