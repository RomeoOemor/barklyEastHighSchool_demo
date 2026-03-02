from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import bcrypt
from emergentintegrations.llm.chat import LlmChat, UserMessage
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# ==================== MODELS ====================
class Student(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password: str
    name: str
    grade: str
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    friends: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StudentCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    grade: str

class StudentLogin(BaseModel):
    email: EmailStr
    password: str

class StudentProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    grade: str
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    friends: List[str] = Field(default_factory=list)

class Mark(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    subject: str
    marks: float
    total_marks: float
    term: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Homework(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    subject: str
    description: str
    due_date: str
    grade: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class HomeworkSubmission(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    homework_id: str
    student_id: str
    content: str
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SickLeave(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    reason: str
    start_date: str
    end_date: str
    doctor_note: Optional[str] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TeacherRating(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    teacher_id: str
    student_id: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Teacher(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subject: str
    bio: Optional[str] = None
    profile_image: Optional[str] = None

class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    date: str
    time: str
    location: str
    category: str
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BlogPost(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    student_name: str
    title: str
    content: str
    likes: int = 0
    comments: List[dict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Uniform(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    image_url: str
    sizes: List[str]
    category: str

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class NewsItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    category: str
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Award(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recipient_name: str
    recipient_type: str
    award_title: str
    description: str
    date: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== HELPER FUNCTIONS ====================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ==================== ROUTES ====================

# Authentication
@api_router.post("/auth/register", response_model=StudentProfile)
async def register(student: StudentCreate):
    existing = await db.students.find_one({"email": student.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    student_obj = Student(
        email=student.email,
        password=hash_password(student.password),
        name=student.name,
        grade=student.grade
    )
    
    doc = student_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.students.insert_one(doc)
    
    return StudentProfile(**{k: v for k, v in student_obj.model_dump().items() if k != 'password'})

@api_router.post("/auth/login", response_model=StudentProfile)
async def login(credentials: StudentLogin):
    student = await db.students.find_one({"email": credentials.email}, {"_id": 0})
    if not student or not verify_password(credentials.password, student['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return StudentProfile(**{k: v for k, v in student.items() if k != 'password'})

# Student Profile
@api_router.get("/students/{student_id}", response_model=StudentProfile)
async def get_student(student_id: str):
    student = await db.students.find_one({"id": student_id}, {"_id": 0, "password": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentProfile(**student)

@api_router.put("/students/{student_id}")
async def update_student(student_id: str, bio: Optional[str] = None, interests: Optional[List[str]] = None):
    update_data = {}
    if bio is not None:
        update_data["bio"] = bio
    if interests is not None:
        update_data["interests"] = interests
    
    await db.students.update_one({"id": student_id}, {"$set": update_data})
    return {"message": "Profile updated"}

@api_router.get("/students", response_model=List[StudentProfile])
async def get_all_students():
    students = await db.students.find({}, {"_id": 0, "password": 0}).to_list(1000)
    return [StudentProfile(**s) for s in students]

# Marks
@api_router.get("/marks/{student_id}", response_model=List[Mark])
async def get_marks(student_id: str):
    marks = await db.marks.find({"student_id": student_id}, {"_id": 0}).to_list(1000)
    for mark in marks:
        if isinstance(mark['date'], str):
            mark['date'] = datetime.fromisoformat(mark['date'])
    return marks

@api_router.post("/marks", response_model=Mark)
async def create_mark(mark: Mark):
    doc = mark.model_dump()
    doc['date'] = doc['date'].isoformat()
    await db.marks.insert_one(doc)
    return mark

# Homework
@api_router.get("/homework/{grade}", response_model=List[Homework])
async def get_homework(grade: str):
    homework = await db.homework.find({"grade": grade}, {"_id": 0}).to_list(1000)
    for hw in homework:
        if isinstance(hw['created_at'], str):
            hw['created_at'] = datetime.fromisoformat(hw['created_at'])
    return homework

@api_router.post("/homework", response_model=Homework)
async def create_homework(homework: Homework):
    doc = homework.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.homework.insert_one(doc)
    return homework

@api_router.post("/homework/submit")
async def submit_homework(submission: HomeworkSubmission):
    doc = submission.model_dump()
    doc['submitted_at'] = doc['submitted_at'].isoformat()
    await db.homework_submissions.insert_one(doc)
    return {"message": "Homework submitted successfully"}

# Sick Leave
@api_router.post("/sick-leave")
async def create_sick_leave(leave: SickLeave):
    doc = leave.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.sick_leaves.insert_one(doc)
    return {"message": "Sick leave submitted successfully", "id": leave.id}

@api_router.get("/sick-leave/{student_id}")
async def get_sick_leaves(student_id: str):
    leaves = await db.sick_leaves.find({"student_id": student_id}, {"_id": 0}).to_list(1000)
    return leaves

# Teachers
@api_router.get("/teachers", response_model=List[Teacher])
async def get_teachers():
    teachers = await db.teachers.find({}, {"_id": 0}).to_list(1000)
    return teachers

@api_router.post("/teachers/rate")
async def rate_teacher(rating: TeacherRating):
    doc = rating.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.teacher_ratings.insert_one(doc)
    return {"message": "Rating submitted successfully"}

@api_router.get("/teachers/{teacher_id}/ratings")
async def get_teacher_ratings(teacher_id: str):
    ratings = await db.teacher_ratings.find({"teacher_id": teacher_id}, {"_id": 0}).to_list(1000)
    if not ratings:
        return {"average": 0, "count": 0}
    avg = sum(r['rating'] for r in ratings) / len(ratings)
    return {"average": round(avg, 1), "count": len(ratings), "ratings": ratings}

# Events
@api_router.get("/events", response_model=List[Event])
async def get_events():
    events = await db.events.find({}, {"_id": 0}).to_list(1000)
    for event in events:
        if isinstance(event.get('created_at'), str):
            event['created_at'] = datetime.fromisoformat(event['created_at'])
    return events

@api_router.post("/events", response_model=Event)
async def create_event(event: Event):
    doc = event.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.events.insert_one(doc)
    return event

# Blog Posts
@api_router.get("/blog", response_model=List[BlogPost])
async def get_blog_posts():
    posts = await db.blog_posts.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for post in posts:
        if isinstance(post.get('created_at'), str):
            post['created_at'] = datetime.fromisoformat(post['created_at'])
    return posts

@api_router.post("/blog", response_model=BlogPost)
async def create_blog_post(post: BlogPost):
    doc = post.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.blog_posts.insert_one(doc)
    return post

@api_router.post("/blog/{post_id}/like")
async def like_post(post_id: str):
    await db.blog_posts.update_one({"id": post_id}, {"$inc": {"likes": 1}})
    return {"message": "Post liked"}

@api_router.post("/blog/{post_id}/comment")
async def comment_on_post(post_id: str, comment: dict):
    await db.blog_posts.update_one({"id": post_id}, {"$push": {"comments": comment}})
    return {"message": "Comment added"}

# Uniforms
@api_router.get("/uniforms", response_model=List[Uniform])
async def get_uniforms():
    uniforms = await db.uniforms.find({}, {"_id": 0}).to_list(1000)
    return uniforms

@api_router.post("/uniforms/purchase")
async def purchase_uniform(order: dict):
    order['id'] = str(uuid.uuid4())
    order['created_at'] = datetime.now(timezone.utc).isoformat()
    order['status'] = 'completed'
    await db.orders.insert_one(order)
    return {"message": "Order placed successfully", "order_id": order['id']}

# News
@api_router.get("/news", response_model=List[NewsItem])
async def get_news():
    news = await db.news.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for item in news:
        if isinstance(item.get('created_at'), str):
            item['created_at'] = datetime.fromisoformat(item['created_at'])
    return news

# Awards
@api_router.get("/awards", response_model=List[Award])
async def get_awards():
    awards = await db.awards.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for award in awards:
        if isinstance(award.get('created_at'), str):
            award['created_at'] = datetime.fromisoformat(award['created_at'])
    return awards

# Chatbot
@api_router.post("/chat")
async def chat(message: ChatMessage):
    try:
        chat_instance = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=message.session_id,
            system_message="""You are a helpful assistant for Barkly East High School in the Eastern Cape, South Africa. 
            You can help with questions about:
            - Admissions and enrollment
            - Academic programs and subjects
            - Sports and extracurricular activities
            - School fees and payments
            - Events and important dates
            - General school information
            Be friendly, professional, and helpful."""
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=message.message)
        response = await chat_instance.send_message(user_message)
        
        return {"response": response}
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Emergency Contacts
@api_router.get("/emergency-contacts")
async def get_emergency_contacts():
    return [
        {"id": "1", "type": "Medic/Ambulance", "number": "10177", "description": "Emergency medical services"},
        {"id": "2", "type": "Fire Emergency", "number": "10111", "description": "Fire department emergency line"},
        {"id": "3", "type": "School Security", "number": "+27 11 555 0100", "description": "24/7 school security"},
        {"id": "4", "type": "Poison Control", "number": "0800 333 444", "description": "Poison information center"}
    ]

# Include router
app.include_router(api_router)

# Serve static files from frontend/public directory
from fastapi.staticfiles import StaticFiles
static_dir = ROOT_DIR.parent / "frontend" / "public"
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()