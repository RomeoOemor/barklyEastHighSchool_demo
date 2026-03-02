import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def seed_database():
    print("Seeding database...")
    
    # Clear existing data
    await db.teachers.delete_many({})
    await db.homework.delete_many({})
    await db.events.delete_many({})
    await db.news.delete_many({})
    await db.awards.delete_many({})
    await db.uniforms.delete_many({})
    
    # Seed Teachers
    teachers = [
        {
            "id": "t1",
            "name": "Dr. Sarah Mitchell",
            "subject": "Mathematics",
            "bio": "15 years of teaching experience",
            "profile_image": None
        },
        {
            "id": "t2",
            "name": "Mr. James Anderson",
            "subject": "Science",
            "bio": "Former research scientist",
            "profile_image": None
        },
        {
            "id": "t3",
            "name": "Ms. Emily Chen",
            "subject": "English",
            "bio": "Published author and educator",
            "profile_image": None
        },
        {
            "id": "t4",
            "name": "Mr. David Brown",
            "subject": "History",
            "bio": "History enthusiast with PhD",
            "profile_image": None
        }
    ]
    await db.teachers.insert_many(teachers)
    print(f"✓ Added {len(teachers)} teachers")
    
    # Seed Homework
    homework = [
        {
            "id": "hw1",
            "title": "Algebra Assignment",
            "subject": "Mathematics",
            "description": "Complete exercises 1-20 from Chapter 5",
            "due_date": "2024-02-15",
            "grade": "Grade 10",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "hw2",
            "title": "Science Lab Report",
            "subject": "Science",
            "description": "Write a report on the photosynthesis experiment",
            "due_date": "2024-02-18",
            "grade": "Grade 10",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "hw3",
            "title": "Essay Writing",
            "subject": "English",
            "description": "Write a 500-word essay on climate change",
            "due_date": "2024-02-20",
            "grade": "Grade 10",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    await db.homework.insert_many(homework)
    print(f"✓ Added {len(homework)} homework assignments")
    
    # Seed Events
    events = [
        {
            "id": "e1",
            "title": "Annual Sports Day",
            "description": "Join us for a day of athletic competitions and fun!",
            "date": "2024-03-15",
            "time": "9:00 AM",
            "location": "Main Sports Field",
            "category": "Sports",
            "image_url": "https://images.unsplash.com/photo-1763561950978-2675d755f80a",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "e2",
            "title": "Science Fair",
            "description": "Showcase your scientific projects and innovations",
            "date": "2024-03-20",
            "time": "2:00 PM",
            "location": "School Auditorium",
            "category": "Academic",
            "image_url": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "e3",
            "title": "Prize Giving Ceremony",
            "description": "Annual awards ceremony celebrating excellence",
            "date": "2024-04-05",
            "time": "6:00 PM",
            "location": "Main Hall",
            "category": "Awards",
            "image_url": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    await db.events.insert_many(events)
    print(f"✓ Added {len(events)} events")
    
    # Seed News
    news = [
        {
            "id": "n1",
            "title": "School Wins Regional Championship",
            "content": "Our soccer team has won the regional championship after an exciting final match. Congratulations to the team!",
            "category": "Sports",
            "image_url": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "n2",
            "title": "New Computer Lab Opening",
            "content": "We're excited to announce the opening of our new state-of-the-art computer lab with the latest technology.",
            "category": "Academics",
            "image_url": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "n3",
            "title": "Upcoming Parent-Teacher Meeting",
            "content": "Mark your calendars for the parent-teacher conference scheduled for next month.",
            "category": "General",
            "image_url": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    await db.news.insert_many(news)
    print(f"✓ Added {len(news)} news items")
    
    # Seed Awards
    awards = [
        {
            "id": "a1",
            "recipient_name": "Sarah Johnson",
            "recipient_type": "Student",
            "award_title": "Academic Excellence Award",
            "description": "Outstanding performance in Grade 10 examinations",
            "date": "2024-01-15",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "a2",
            "recipient_name": "Michael Chen",
            "recipient_type": "Student",
            "award_title": "Sports Achievement Award",
            "description": "Exceptional performance in regional athletics",
            "date": "2024-01-20",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "a3",
            "recipient_name": "Dr. Sarah Mitchell",
            "recipient_type": "Teacher",
            "award_title": "Teacher of the Year",
            "description": "Outstanding dedication to student success",
            "date": "2024-01-25",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    await db.awards.insert_many(awards)
    print(f"✓ Added {len(awards)} awards")
    
    # Seed Uniforms
    uniforms = [
        {
            "id": "u1",
            "name": "School Blazer",
            "description": "Official school blazer with emblem",
            "price": 89.99,
            "image_url": "https://images.unsplash.com/photo-1666358067414-c77508c771b2?w=400",
            "sizes": ["S", "M", "L", "XL"],
            "category": "Uniform"
        },
        {
            "id": "u2",
            "name": "White School Shirt",
            "description": "Crisp white cotton shirt",
            "price": 29.99,
            "image_url": "https://images.unsplash.com/photo-1666358067414-c77508c771b2?w=400",
            "sizes": ["S", "M", "L", "XL"],
            "category": "Uniform"
        },
        {
            "id": "u3",
            "name": "School Tie",
            "description": "School colors striped tie",
            "price": 15.99,
            "image_url": "https://images.unsplash.com/photo-1666358067414-c77508c771b2?w=400",
            "sizes": ["One Size"],
            "category": "Accessory"
        }
    ]
    await db.uniforms.insert_many(uniforms)
    print(f"✓ Added {len(uniforms)} uniform items")
    
    print("\n✅ Database seeded successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
