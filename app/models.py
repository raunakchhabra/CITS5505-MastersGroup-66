from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, Boolean, DateTime, ForeignKey
from app.extensions import db
from enum import Enum
from sqlalchemy import Enum as SAEnum, JSON, String


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    role: Mapped[str] = mapped_column(Text, default="student", nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    app_language: Mapped[str] = mapped_column(Text, default="en", nullable=False)
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    receive_reminder: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    receive_email: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationship
    courses: Mapped[list["Course"]] = relationship("Course", back_populates="teacher")
    user_languages: Mapped[list["Userlanguage"]] = relationship("Userlanguage", back_populates="user")
    progress: Mapped[list["Progress"]] = relationship("Progress", back_populates="user")
    enrollments: Mapped[list["Enrollment"]] = relationship("Enrollment", back_populates="user")
    studylogs: Mapped[list["Studylog"]] = relationship("Studylog", back_populates="user")
    exercise_submissions: Mapped[list["Exercisesubmission"]] = relationship("Exercisesubmission", back_populates="user")
    user_achievements: Mapped[list["Userachievement"]] = relationship("Userachievement", back_populates="user")
    forum_posts: Mapped[list["Forumpost"]] = relationship("Forumpost", back_populates="user")
    friendships: Mapped[list["Friendship"]] = relationship("Friendship", foreign_keys='Friendship.user_id',
                                                           back_populates="user")
    friends_of: Mapped[list["Friendship"]] = relationship("Friendship", foreign_keys='Friendship.friend_id',
                                                          back_populates="friend")
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="user")
    share_groups: Mapped[list["Sharegroup"]] = relationship("Sharegroup", back_populates="owner")
    share_group_memberships: Mapped[list["Sharegroupmember"]] = relationship("Sharegroupmember", back_populates="user")
    shared_records: Mapped[list["Sharerecord"]] = relationship("Sharerecord", foreign_keys='Sharerecord.owner_id',
                                                               back_populates="owner")
    shared_with_me: Mapped[list["Sharerecord"]] = relationship("Sharerecord", foreign_keys='Sharerecord.target_user_id',
                                                               back_populates="target_user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class Course(db.Model):
    __tablename__ = 'course'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))

    teacher: Mapped["User"] = relationship("User", back_populates="courses")
    exercises: Mapped[list["Exercise"]] = relationship("Exercise", back_populates="course")
    progress: Mapped[list["Progress"]] = relationship("Progress", back_populates="course")
    enrollments: Mapped[list["Enrollment"]] = relationship("Enrollment", back_populates="course")


class Userlanguage(db.Model):
    __tablename__ = 'userlanguage'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    language: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean)

    user: Mapped["User"] = relationship("User", back_populates="user_languages")


class Progress(db.Model):
    __tablename__ = 'progress'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey('course.id'))
    date: Mapped[str] = mapped_column(Text)
    listening: Mapped[int] = mapped_column(Integer)
    reading: Mapped[int] = mapped_column(Integer)
    speaking: Mapped[int] = mapped_column(Integer)
    writing: Mapped[int] = mapped_column(Integer)
    vocabulary_count: Mapped[int] = mapped_column(Integer)
    level: Mapped[str] = mapped_column(Text)
    total_study_hours: Mapped[str] = mapped_column(Text)

    user: Mapped["User"] = relationship("User", back_populates="progress")
    course: Mapped["Course"] = relationship("Course", back_populates="progress")


class Enrollment(db.Model):
    __tablename__ = 'enrollment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey('course.id'))
    enrolled_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="enrollments")
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")


class Studylog(db.Model):
    __tablename__ = 'studylog'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    date: Mapped[str] = mapped_column(Text)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    activity_type: Mapped[str] = mapped_column(Text)
    skills: Mapped[str] = mapped_column(Text)
    notes: Mapped[str] = mapped_column(Text)
    rating: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="studylogs")


class Exercise(db.Model):
    __tablename__ = 'exercise'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey('course.id'))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(Text)

    course: Mapped["Course"] = relationship("Course", back_populates="exercises")
    submissions: Mapped[list["Exercisesubmission"]] = relationship("Exercisesubmission", back_populates="exercise")


class Exercisesubmission(db.Model):
    __tablename__ = 'exercisesubmission'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    exercise_id: Mapped[int] = mapped_column(Integer, ForeignKey('exercise.id'))
    submitted_answer: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="exercise_submissions")
    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="submissions")


class Achievement(db.Model):
    __tablename__ = 'achievement'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    icon: Mapped[str] = mapped_column(Text)

    user_achievements: Mapped[list["Userachievement"]] = relationship("Userachievement", back_populates="achievement")


class Userachievement(db.Model):
    __tablename__ = 'userachievement'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    achievement_id: Mapped[int] = mapped_column(Integer, ForeignKey('achievement.id'))
    achieved_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="user_achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")


class Forumpost(db.Model):
    __tablename__ = 'forumpost'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="forum_posts")


class Friendship(db.Model):
    __tablename__ = 'friendship'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    friend_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="friendships")
    friend: Mapped["User"] = relationship("User", foreign_keys=[friend_id], back_populates="friends_of")


class Recommendation(db.Model):
    __tablename__ = 'recommendation'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="recommendations")


class Sharegroup(db.Model):
    __tablename__ = 'sharegroup'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner: Mapped["User"] = relationship("User", back_populates="share_groups")
    members: Mapped[list["Sharegroupmember"]] = relationship("Sharegroupmember", back_populates="group")


class Sharegroupmember(db.Model):
    __tablename__ = 'sharegroupmember'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('sharegroup.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    group: Mapped["Sharegroup"] = relationship("Sharegroup", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="share_group_memberships")


class Sharerecord(db.Model):
    __tablename__ = 'sharerecord'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    target_user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    data_type: Mapped[str] = mapped_column(Text)
    data_content: Mapped[str] = mapped_column(Text)
    shared_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id], back_populates="shared_records")
    target_user: Mapped["User"] = relationship("User", foreign_keys=[target_user_id], back_populates="shared_with_me")


class DataType(Enum):
    VOCABULARY = "vocabulary"
    STUDY_TIME = "study_time"
    ASSESSMENT = "assessment"
    OTHER = "other"


class Data(db.Model):
    __tablename__ = "data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    data_type: Mapped[DataType] = mapped_column(SAEnum(DataType), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    file_path: Mapped[str] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    extra_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    shared_data: Mapped[list["SharedData"]] = relationship("SharedData", back_populates="data")

    def __repr__(self):
        return f"<Data {self.title}>"


class SharedPermission(Enum):
    READ = "read"
    EDIT = "edit"


class SharedData(db.Model):
    __tablename__ = "shareddata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data_id: Mapped[int] = mapped_column(Integer, ForeignKey("data.id"), nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    permission: Mapped[SharedPermission] = mapped_column(SAEnum(SharedPermission), default=SharedPermission.READ)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    data: Mapped["Data"] = relationship("Data", back_populates="shared_data")
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id], backref="shared_data_owned")
    recipient: Mapped["User"] = relationship("User", foreign_keys=[recipient_id], backref="shared_data_received")

    def __repr__(self):
        return f"<SharedData {self.id}>"