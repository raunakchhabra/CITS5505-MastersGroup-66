from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, Boolean, DateTime, ForeignKey
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped = mapped_column(Text)
    email: Mapped = mapped_column(Text, unique=True)
    password_hash: Mapped = mapped_column(Text)
    role: Mapped = mapped_column(Text, default="student")
    xp: Mapped = mapped_column(Integer)
    streak_days: Mapped = mapped_column(Integer)
    app_language: Mapped = mapped_column(Text)
    daily_goal_minutes: Mapped = mapped_column(Integer)
    receive_reminder: Mapped = mapped_column(Boolean)
    receive_email: Mapped = mapped_column(Boolean)

    courses = relationship("Course", back_populates="teacher")
    user_languages = relationship("Userlanguage", back_populates="user")
    progress = relationship("Progress", back_populates="user")
    enrollments = relationship("Enrollment", back_populates="user")
    studylogs = relationship("Studylog", back_populates="user")
    exercise_submissions = relationship("Exercisesubmission", back_populates="user")
    user_achievements = relationship("Userachievement", back_populates="user")
    forum_posts = relationship("Forumpost", back_populates="user")
    friendships = relationship("Friendship", foreign_keys='Friendship.user_id', back_populates="user")
    friends_of = relationship("Friendship", foreign_keys='Friendship.friend_id', back_populates="friend")
    recommendations = relationship("Recommendation", back_populates="user")
    share_groups = relationship("Sharegroup", back_populates="owner")
    share_group_memberships = relationship("Sharegroupmember", back_populates="user")
    shared_records = relationship("Sharerecord", foreign_keys='Sharerecord.owner_id', back_populates="owner")
    shared_with_me = relationship("Sharerecord", foreign_keys='Sharerecord.target_user_id', back_populates="target_user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class Course(db.Model):
    __tablename__ = 'course'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped = mapped_column(Text)
    language: Mapped = mapped_column(Text)
    level: Mapped = mapped_column(Text)
    description: Mapped = mapped_column(Text)
    teacher_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))

    teacher = relationship("User", back_populates="courses")
    exercises = relationship("Exercise", back_populates="course")
    progress = relationship("Progress", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")


class Userlanguage(db.Model):
    __tablename__ = 'userlanguage'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    language: Mapped = mapped_column(Text)
    level: Mapped = mapped_column(Text)
    is_active: Mapped = mapped_column(Boolean)

    user = relationship("User", back_populates="user_languages")


class Progress(db.Model):
    __tablename__ = 'progress'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    course_id: Mapped = mapped_column(Integer, ForeignKey('course.id'))
    date: Mapped = mapped_column(Text)
    listening: Mapped = mapped_column(Integer)
    reading: Mapped = mapped_column(Integer)
    speaking: Mapped = mapped_column(Integer)
    writing: Mapped = mapped_column(Integer)
    vocabulary_count: Mapped = mapped_column(Integer)
    level: Mapped = mapped_column(Text)
    total_study_hours: Mapped = mapped_column(Text)

    user = relationship("User", back_populates="progress")
    course = relationship("Course", back_populates="progress")


class Enrollment(db.Model):
    __tablename__ = 'enrollment'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    course_id: Mapped = mapped_column(Integer, ForeignKey('course.id'))
    enrolled_at: Mapped = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class Studylog(db.Model):
    __tablename__ = 'studylog'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    date: Mapped = mapped_column(Text)
    duration_minutes: Mapped = mapped_column(Integer)
    activity_type: Mapped = mapped_column(Text)
    skills: Mapped = mapped_column(Text)
    notes: Mapped = mapped_column(Text)
    rating: Mapped = mapped_column(Integer)
    created_at: Mapped = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="studylogs")


class Exercise(db.Model):
    __tablename__ = 'exercise'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    course_id: Mapped = mapped_column(Integer, ForeignKey('course.id'))
    question: Mapped = mapped_column(Text)
    correct_option: Mapped = mapped_column(Text)
    lesson_number: Mapped = mapped_column(Integer)

    course = relationship("Course", back_populates="exercises")
    submissions = relationship("Exercisesubmission", back_populates="exercise")


class Exercisesubmission(db.Model):
    __tablename__ = 'exercisesubmission'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    exercise_id: Mapped = mapped_column(Integer, ForeignKey('exercise.id'))
    selected_option: Mapped = mapped_column(Text)
    is_correct: Mapped = mapped_column(Boolean)
    submitted_at: Mapped = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="exercise_submissions")
    exercise = relationship("Exercise", back_populates="submissions")


class Achievement(db.Model):
    __tablename__ = 'achievement'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    title: Mapped = mapped_column(Text)
    description: Mapped = mapped_column(Text)

    user_achievements = relationship("Userachievement", back_populates="achievement")


class Userachievement(db.Model):
    __tablename__ = 'userachievement'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    achievement_id: Mapped = mapped_column(Integer, ForeignKey('achievement.id'))
    earned_at: Mapped = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")


class Forumpost(db.Model):
    __tablename__ = 'forumpost'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    title: Mapped = mapped_column(Text)
    content: Mapped = mapped_column(Text)
    posted_at: Mapped = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="forum_posts")


class Friendship(db.Model):
    __tablename__ = 'friendship'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    friend_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    created_at: Mapped = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", foreign_keys=[user_id], back_populates="friendships")
    friend = relationship("User", foreign_keys=[friend_id], back_populates="friends_of")


class Recommendation(db.Model):
    __tablename__ = 'recommendation'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    message: Mapped = mapped_column(Text)
    category: Mapped = mapped_column(Text)
    created_at: Mapped = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="recommendations")


class Sharegroup(db.Model):
    __tablename__ = 'sharegroup'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    owner_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    name: Mapped = mapped_column(Text)
    description: Mapped = mapped_column(Text)
    created_at: Mapped = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="share_groups")
    members = relationship("Sharegroupmember", back_populates="group")
    shared_records = relationship("Sharerecord", back_populates="group")


class Sharegroupmember(db.Model):
    __tablename__ = 'sharegroupmember'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    group_id: Mapped = mapped_column(Integer, ForeignKey('sharegroup.id'))
    user_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    joined_at: Mapped = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    group = relationship("Sharegroup", back_populates="members")
    user = relationship("User", back_populates="share_group_memberships")


class Sharerecord(db.Model):
    __tablename__ = 'sharerecord'

    id: Mapped = mapped_column(Integer, primary_key=True, nullable=False)
    owner_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    target_user_id: Mapped = mapped_column(Integer, ForeignKey('user.id'))
    target_group_id: Mapped = mapped_column(Integer, ForeignKey('sharegroup.id'))
    data_types: Mapped = mapped_column(Text)
    access_level: Mapped = mapped_column(Text)
    created_at: Mapped = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", foreign_keys=[owner_id], back_populates="shared_records")
    target_user = relationship("User", foreign_keys=[target_user_id], back_populates="shared_with_me")
    group = relationship("Sharegroup", back_populates="shared_records")
