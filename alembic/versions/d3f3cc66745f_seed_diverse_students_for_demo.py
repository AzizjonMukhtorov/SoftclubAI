"""seed_diverse_students_for_demo

Revision ID: d3f3cc66745f
Revises: cb53a71b9c99
Create Date: 2026-01-03 20:28:35.475000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3f3cc66745f'
down_revision: Union[str, Sequence[str], None] = 'cb53a71b9c99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed 9 diverse students for ML demo (3 Low, 3 Medium, 3 High risk)"""
    
    # Create connection
    connection = op.get_bind()
    
    # Students data (from add_diverse_students.py)
    students = [
        # LOW RISK - Excellent students
        {
            'name': 'Аида Токтарова', 'email': 'aida@example.com', 'course': 'Python Backend',
            'attendance_rate': 95.5, 'homework_completion': 92.0, 'payment_delays': 0,
            'days_since_last_payment': 5, 'test_avg_score': 90.0, 'communication_activity': 18,
            'days_enrolled': 120, 'missed_classes_streak': 0
        },
        {
            'name': 'Бекзат Нурланов', 'email': 'bekzat@example.com', 'course': 'Frontend React',
            'attendance_rate': 88.0, 'homework_completion': 85.0, 'payment_delays': 1,
            'days_since_last_payment': 10, 'test_avg_score': 82.0, 'communication_activity': 12,
            'days_enrolled': 90, 'missed_classes_streak': 1
        },
        {
            'name': 'Гульмира Сапарова', 'email': 'gulmira@example.com', 'course': 'Data Science',
            'attendance_rate': 92.0, 'homework_completion': 88.0, 'payment_delays': 0,
            'days_since_last_payment': 3, 'test_avg_score': 87.0, 'communication_activity': 15,
            'days_enrolled': 150, 'missed_classes_streak': 0
        },
        
        # MEDIUM RISK - Borderline students
        {
            'name': 'Данияр Ыскаков', 'email': 'daniyar@example.com', 'course': 'Mobile Development',
            'attendance_rate': 65.0, 'homework_completion': 55.0, 'payment_delays': 2,
            'days_since_last_payment': 25, 'test_avg_score': 62.0, 'communication_activity': 5,
            'days_enrolled': 60, 'missed_classes_streak': 3
        },
        {
            'name': 'Елена Ким', 'email': 'elena@example.com', 'course': 'DevOps',
            'attendance_rate': 70.0, 'homework_completion': 68.0, 'payment_delays': 3,
            'days_since_last_payment': 30, 'test_avg_score': 65.0, 'communication_activity': 6,
            'days_enrolled': 75, 'missed_classes_streak': 2
        },
        {
            'name': 'Жанар Асанова', 'email': 'zhanar@example.com', 'course': 'Python Backend',
            'attendance_rate': 58.0, 'homework_completion': 60.0, 'payment_delays': 2,
            'days_since_last_payment': 20, 'test_avg_score': 58.0, 'communication_activity': 4,
            'days_enrolled': 45, 'missed_classes_streak': 4
        },
        
        # HIGH RISK - At-risk students
        {
            'name': 'Искандер Ормонов', 'email': 'iskander@example.com', 'course': 'Frontend React',
            'attendance_rate': 35.0, 'homework_completion': 30.0, 'payment_delays': 5,
            'days_since_last_payment': 50, 'test_avg_score': 42.0, 'communication_activity': 1,
            'days_enrolled': 40, 'missed_classes_streak': 7
        },
        {
            'name': 'Камила Джунусова', 'email': 'kamila@example.com', 'course': 'Data Science',
            'attendance_rate': 28.0, 'homework_completion': 25.0, 'payment_delays': 6,
            'days_since_last_payment': 60, 'test_avg_score': 38.0, 'communication_activity': 0,
            'days_enrolled': 30, 'missed_classes_streak': 8
        },
        {
            'name': 'Луис Мамбеталиев', 'email': 'luis@example.com', 'course': 'Mobile Development',
            'attendance_rate': 42.0, 'homework_completion': 38.0, 'payment_delays': 4,
            'days_since_last_payment': 45, 'test_avg_score': 45.0, 'communication_activity': 2,
            'days_enrolled': 50, 'missed_classes_streak': 6
        },
    ]
    
    # Insert students
    for student in students:
        connection.execute(
            sa.text("""
                INSERT INTO students (
                    name, email, course, attendance_rate, homework_completion,
                    payment_delays, days_since_last_payment, test_avg_score,
                    communication_activity, days_enrolled, missed_classes_streak
                ) VALUES (
                    :name, :email, :course, :attendance_rate, :homework_completion,
                    :payment_delays, :days_since_last_payment, :test_avg_score,
                    :communication_activity, :days_enrolled, :missed_classes_streak
                )
            """),
            student
        )


def downgrade() -> None:
    """Remove seeded students"""
    connection = op.get_bind()
    
    # Delete only the students we added (by email pattern)
    emails = [
        'aida@example.com', 'bekzat@example.com', 'gulmira@example.com',
        'daniyar@example.com', 'elena@example.com', 'zhanar@example.com',
        'iskander@example.com', 'kamila@example.com', 'luis@example.com'
    ]
    
    for email in emails:
        connection.execute(
            sa.text("DELETE FROM students WHERE email = :email"),
            {'email': email}
        )
