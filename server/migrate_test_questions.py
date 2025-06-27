#!/usr/bin/env python3
"""
Migration script để chuyển đổi test questions từ dict format sang array format
"""

import sys
import os

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after path setup to avoid import errors
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.test_model import Test
    from app.core.config import settings
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the server directory")
    sys.exit(1)


def migrate_test_questions():
    """
    Migrate test questions from dict format to array format
    """
    # Create synchronous engine for migration
    engine = create_engine(settings.DATABASE_URI)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        # Get all tests
        tests = session.query(Test).all()

        migrated_count = 0

        for test in tests:
            if test.questions and isinstance(test.questions, dict):
                # Check if it's the old format (dict with keys like q1, q2, etc.)
                if all(key.startswith("q") for key in test.questions.keys() if key):
                    print(f"Migrating test ID {test.id}...")

                    # Convert to array format
                    questions_list = []
                    for key in sorted(test.questions.keys()):
                        question = test.questions[key]
                        questions_list.append(question)

                    # Update the test
                    test.questions = questions_list
                    migrated_count += 1

                    print(
                        f"  - Converted {len(questions_list)} questions from dict to array"
                    )

        if migrated_count > 0:
            session.commit()
            print(f"\nSuccessfully migrated {migrated_count} tests!")
        else:
            print("No tests needed migration.")


if __name__ == "__main__":
    print("Starting test questions migration...")
    try:
        migrate_test_questions()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
