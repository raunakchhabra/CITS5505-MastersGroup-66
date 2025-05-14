from flask import Blueprint, jsonify, request, url_for
from flask_login import login_required, current_user
from app.models import (db, User, Data, SharedData, Sharegroup, Sharegroupmember,
                        SharedPermission, DataType)
from sqlalchemy import or_

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/shared_users')
@login_required
def shared_users():
    """Get users with whom data is shared"""
    shared_users = db.session.query(User, SharedData).join(
        SharedData, SharedData.recipient_id == User.id
    ).filter(
        SharedData.owner_id == current_user.id
    ).distinct(User.id).all()

    users = []
    for user, shared_data in shared_users:
        # Get all data types shared with this user
        shared_types = db.session.query(Data.data_type).join(
            SharedData, SharedData.data_id == Data.id
        ).filter(
            SharedData.owner_id == current_user.id,
            SharedData.recipient_id == user.id
        ).distinct().all()

        users.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'permission': shared_data.permission.value,
            'shared_data': [
                {
                    'type': data_type[0].value,
                    'label': data_type[0].value.replace('_', ' ').title(),
                    'shared': True
                }
                for data_type in shared_types
            ]
        })

    return jsonify({'users': users})


@api_bp.route('/share_groups')
@login_required
def share_groups():
    """Get user's share groups"""
    # Groups owned by user
    owned_groups = Sharegroup.query.filter_by(owner_id=current_user.id).all()

    # Groups user is member of
    member_groups = db.session.query(Sharegroup).join(
        Sharegroupmember, Sharegroupmember.group_id == Sharegroup.id
    ).filter(Sharegroupmember.user_id == current_user.id).all()

    all_groups = list(set(owned_groups + member_groups))

    groups = []
    for group in all_groups:
        member_count = Sharegroupmember.query.filter_by(group_id=group.id).count()

        groups.append({
            'id': group.id,
            'name': group.name,
            'description': '',  # Add description field to Sharegroup model if needed
            'member_count': member_count,
            'is_owner': group.owner_id == current_user.id,
            'shared_data': [
                {
                    'type': 'vocabulary',
                    'label': 'Vocabulary',
                    'shared': True
                },
                {
                    'type': 'study_time',
                    'label': 'Study Time',
                    'shared': True
                }
            ]
        })

    return jsonify({'groups': groups})


@api_bp.route('/shared_with_me')
@login_required
def shared_with_me():
    """Get data shared with current user"""
    shared_data = db.session.query(Data, SharedData, User).join(
        SharedData, SharedData.data_id == Data.id
    ).join(
        User, User.id == SharedData.owner_id
    ).filter(
        SharedData.recipient_id == current_user.id
    ).all()

    data_list = []
    for data, shared, owner in shared_data:
        data_list.append({
            'id': data.id,
            'title': data.title,
            'data_type': data.data_type.value,
            'owner_name': owner.name,
            'created_at': shared.created_at.isoformat(),
            'permission': shared.permission.value,
            'view_url': url_for('data_bp.view', id=data.id)
        })

    return jsonify({'shared_data': data_list})


@api_bp.route('/share_history')
@login_required
def share_history():
    """Get sharing history"""
    history = db.session.query(SharedData, Data, User).join(
        Data, SharedData.data_id == Data.id
    ).join(
        User, User.id == SharedData.recipient_id
    ).filter(
        SharedData.owner_id == current_user.id
    ).order_by(SharedData.created_at.desc()).limit(20).all()

    history_items = []
    for shared, data, recipient in history:
        history_items.append({
            'id': shared.id,
            'title': f"Shared {data.title} with {recipient.name}",
            'description': f"You shared {data.data_type.value.replace('_', ' ')} data",
            'created_at': shared.created_at.isoformat(),
            'permission': shared.permission.value
        })

    return jsonify({'history': history_items})


@api_bp.route('/quick_share_groups')
@login_required
def quick_share_groups():
    """Get quick share groups"""
    groups = Sharegroup.query.filter_by(owner_id=current_user.id).limit(3).all()

    group_list = [
        {
            'id': group.id,
            'name': group.name
        }
        for group in groups
    ]

    return jsonify({'groups': group_list})


@api_bp.route('/my_data_summary')
@login_required
def my_data_summary():
    """Get user's data for sharing"""
    user_data = Data.query.filter_by(user_id=current_user.id).order_by(Data.created_at.desc()).all()

    data_items = []
    for data in user_data:
        data_items.append({
            'id': data.id,
            'title': data.title,
            'data_type': data.data_type.value,
            'description': data.description
        })

    return jsonify({'data_items': data_items})


@api_bp.route('/search_users')
@login_required
def search_users():
    """Search users for sharing"""
    query = request.args.get('q', '').strip()

    if len(query) < 2:
        return jsonify({'users': []})

    users = User.query.filter(
        User.id != current_user.id,
        or_(
            User.name.ilike(f'%{query}%'),
            User.email.ilike(f'%{query}%')
        )
    ).limit(10).all()

    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'name': user.name,
            'email': user.email
        })

    return jsonify({'users': user_list})


@api_bp.route('/share_data', methods=['POST'])
@login_required
def share_data():
    """Share data with users"""
    data = request.get_json()

    recipient_id = data.get('recipient_id')
    recipient_email = data.get('recipient_email')
    data_ids = data.get('data_ids', [])
    permission = data.get('permission', 'read')
    message = data.get('message', '')

    if not data_ids:
        return jsonify({'error': 'No data selected for sharing'}), 400

    # If no recipient_id, try to find user by email
    if not recipient_id and recipient_email:
        recipient = User.query.filter_by(email=recipient_email).first()
        if not recipient:
            return jsonify({'error': 'User not found'}), 404
        recipient_id = recipient.id

    if not recipient_id:
        return jsonify({'error': 'Recipient not specified'}), 400

    # Create shared data entries
    for data_id in data_ids:
        # Check if data belongs to current user
        data_item = Data.query.filter_by(id=data_id, user_id=current_user.id).first()
        if not data_item:
            continue

        # Check if already shared
        existing = SharedData.query.filter_by(
            data_id=data_id,
            owner_id=current_user.id,
            recipient_id=recipient_id
        ).first()

        if existing:
            existing.permission = SharedPermission[permission.upper()]
        else:
            shared_data = SharedData(
                data_id=data_id,
                owner_id=current_user.id,
                recipient_id=recipient_id,
                permission=SharedPermission[permission.upper()]
            )
            db.session.add(shared_data)

    db.session.commit()

    return jsonify({'success': True})


@api_bp.route('/create_group', methods=['POST'])
@login_required
def create_group():
    """Create a new share group"""
    data = request.get_json()

    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Group name is required'}), 400

    # Check if group name already exists for this user
    existing = Sharegroup.query.filter_by(owner_id=current_user.id, name=name).first()
    if existing:
        return jsonify({'error': 'Group with this name already exists'}), 400

    # Create group
    group = Sharegroup(
        owner_id=current_user.id,
        name=name
    )
    db.session.add(group)
    db.session.flush()

    # Add owner as member
    member = Sharegroupmember(
        group_id=group.id,
        user_id=current_user.id
    )
    db.session.add(member)
    db.session.commit()

    return jsonify({'success': True, 'group_id': group.id})


@api_bp.route('/update_sharing/<int:user_id>', methods=['PUT'])
@login_required
def update_sharing(user_id):
    """Update sharing settings with a user"""
    data = request.get_json()

    shared_types = data.get('shared_data', [])
    permission = data.get('permission', 'read')

    # Update existing shares
    shared_data_items = SharedData.query.filter_by(
        owner_id=current_user.id,
        recipient_id=user_id
    ).all()

    for item in shared_data_items:
        item.permission = SharedPermission[permission.upper()]

    db.session.commit()

    return jsonify({'success': True})


@api_bp.route('/revoke_share/<int:user_id>', methods=['DELETE'])
@login_required
def revoke_share(user_id):
    """Revoke all sharing with a user"""
    SharedData.query.filter_by(
        owner_id=current_user.id,
        recipient_id=user_id
    ).delete()

    db.session.commit()

    return jsonify({'success': True})


@api_bp.route('/update_group_sharing/<int:group_id>', methods=['PUT'])
@login_required
def update_group_sharing(group_id):
    """Update group sharing settings"""
    data = request.get_json()

    shared_types = data.get('shared_data', [])

    # For now, just return success
    # In a real implementation, you'd update group-wide sharing settings

    return jsonify({'success': True})


@api_bp.route('/leave_group/<int:group_id>', methods=['DELETE'])
@login_required
def leave_group(group_id):
    """Leave or delete a group"""
    group = Sharegroup.query.get_or_404(group_id)

    if group.owner_id == current_user.id:
        # Delete the group if owner
        Sharegroupmember.query.filter_by(group_id=group_id).delete()
        db.session.delete(group)
    else:
        # Just remove membership
        Sharegroupmember.query.filter_by(
            group_id=group_id,
            user_id=current_user.id
        ).delete()

    db.session.commit()

    return jsonify({'success': True})


@api_bp.route('/group_members/<int:group_id>')
@login_required
def group_members(group_id):
    """Get group members"""
    members = db.session.query(User, Sharegroupmember).join(
        Sharegroupmember, Sharegroupmember.user_id == User.id
    ).filter(
        Sharegroupmember.group_id == group_id
    ).all()

    group = Sharegroup.query.get_or_404(group_id)

    member_list = []
    for user, membership in members:
        member_list.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_owner': user.id == group.owner_id
        })

    return jsonify({'members': member_list})


@api_bp.route('/share_details/<int:share_id>')
@login_required
def share_details(share_id):
    """Get details of a specific share"""
    shared = db.session.query(SharedData, Data, User).join(
        Data, SharedData.data_id == Data.id
    ).join(
        User, User.id == SharedData.recipient_id
    ).filter(
        SharedData.id == share_id,
        SharedData.owner_id == current_user.id
    ).first()

    if not shared:
        return jsonify({'error': 'Share not found'}), 404

    shared_data, data, recipient = shared

    return jsonify({
        'id': shared_data.id,
        'recipient_name': recipient.name,
        'data_type': data.data_type.value,
        'permission': shared_data.permission.value,
        'created_at': shared_data.created_at.isoformat(),
        'message': ''  # Add message field to SharedData model if needed
    })


@api_bp.route('/search_shared_users')
@login_required
def search_shared_users():
    """Search among users with whom data is shared"""
    query = request.args.get('q', '').strip()

    users_query = db.session.query(User, SharedData).join(
        SharedData, SharedData.recipient_id == User.id
    ).filter(
        SharedData.owner_id == current_user.id
    )

    if query:
        users_query = users_query.filter(
            or_(
                User.name.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        )

    shared_users = users_query.distinct(User.id).all()

    users = []
    for user, shared_data in shared_users:
        # Get all data types shared with this user
        shared_types = db.session.query(Data.data_type).join(
            SharedData, SharedData.data_id == Data.id
        ).filter(
            SharedData.owner_id == current_user.id,
            SharedData.recipient_id == user.id
        ).distinct().all()

        users.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'permission': shared_data.permission.value,
            'shared_data': [
                {
                    'type': data_type[0].value,
                    'label': data_type[0].value.replace('_', ' ').title(),
                    'shared': True
                }
                for data_type in shared_types
            ]
        })

    return jsonify({'users': users})


@api_bp.route('/search_groups')
@login_required
def search_groups():
    """Search user's share groups"""
    query = request.args.get('q', '').strip()

    # Base query for groups
    groups_query = db.session.query(Sharegroup).filter(
        or_(
            Sharegroup.owner_id == current_user.id,
            Sharegroup.id.in_(
                db.session.query(Sharegroupmember.group_id).filter(
                    Sharegroupmember.user_id == current_user.id
                )
            )
        )
    )

    if query:
        groups_query = groups_query.filter(
            Sharegroup.name.ilike(f'%{query}%')
        )

    groups = groups_query.all()

    group_list = []
    for group in groups:
        member_count = Sharegroupmember.query.filter_by(group_id=group.id).count()

        group_list.append({
            'id': group.id,
            'name': group.name,
            'description': '',
            'member_count': member_count,
            'is_owner': group.owner_id == current_user.id,
            'shared_data': [
                {
                    'type': 'vocabulary',
                    'label': 'Vocabulary',
                    'shared': True
                },
                {
                    'type': 'study_time',
                    'label': 'Study Time',
                    'shared': True
                }
            ]
        })

    return jsonify({'groups': group_list})