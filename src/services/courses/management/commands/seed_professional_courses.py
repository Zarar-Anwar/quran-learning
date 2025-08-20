from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone

import io
import requests
from PIL import Image

from src.services.courses.models import Course, Instructor


CURATED_COURSES = [
    {
        "title": "Noorani Qaida for Beginners",
        "price": "Free",
        "lessons_count": 24,
        "image_url": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=1600&q=80&auto=format&fit=crop",
        "overview": "Build a strong foundation in Arabic letters, pronunciation and joining rules to start your Quran journey the right way.",
        "description": (
            "This beginner-friendly track covers Arabic alphabets, harakat (vowel marks), sukoon, shaddah, and joining. "
            "By the end, you'll be able to decode Quranic words accurately and read short Surahs with confidence."
        ),
    },
    {
        "title": "Tajweed Mastery (Rules of Recitation)",
        "price": "49/mo",
        "lessons_count": 36,
        "image_url": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=1600&q=80&auto=format&fit=crop",
        "overview": "Master Makharij, Sifaat, Madd, Qalqalah, Ikhfa, Idgham and all core Tajweed rules with practical recitation coaching.",
        "description": (
            "A structured Tajweed curriculum with live feedback. Includes weekly recitation labs, rule drills, and assignments with audio examples."
        ),
    },
    {
        "title": "Quran Memorization (Hifz) Program",
        "price": "Custom Plan",
        "lessons_count": 48,
        "image_url": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=1600&q=80&auto=format&fit=crop",
        "overview": "Personalized Hifz plans tailored to your pace with daily targets, revision cycles and weekly assessments.",
        "description": (
            "Build consistency with a proven methodology: new lesson (sabaq), short-term revision (sabaqi) and long-term consolidation (manzil)."
        ),
    },
    {
        "title": "Arabic for Quranic Understanding",
        "price": "99 one-time",
        "lessons_count": 30,
        "image_url": "https://images.unsplash.com/photo-1508057198894-247b23fe5ade?w=1600&q=80&auto=format&fit=crop",
        "overview": "Learn essential vocabulary and grammar patterns that appear most frequently in the Quran.",
        "description": (
            "Focus on high-frequency Quranic words, verb forms, nominal sentences, and prepositional phrases to understand verses directly."
        ),
    },
    {
        "title": "Tafsir Essentials: Themes of the Quran",
        "price": "29/mo",
        "lessons_count": 20,
        "image_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1600&q=80&auto=format&fit=crop",
        "overview": "Explore core themes: Tawheed, Prophethood, Revelation, Ethics and the Hereafter with classical and modern Tafsir.",
        "description": (
            "Weekly sessions with reading lists from reputable Tafsir. Learn historical context, cross-references and practical takeaways."
        ),
    },
    {
        "title": "Quran Recitation for Kids",
        "price": "19.99",
        "lessons_count": 28,
        "image_url": "https://images.unsplash.com/photo-1596495578065-8a35f76d72da?w=1600&q=80&auto=format&fit=crop",
        "overview": "Child-friendly reading program with games, stickers and short surah goals to keep kids motivated.",
        "description": (
            "Designed for ages 5–12. Includes parent progress dashboards and gentle coaching to improve fluency and love for the Quran."
        ),
    },
    {
        "title": "Ijazah Preparation (Qira'at)",
        "price": "By Assessment",
        "lessons_count": 40,
        "image_url": "https://images.unsplash.com/photo-1491841550275-ad7854e35ca6?w=1600&q=80&auto=format&fit=crop",
        "overview": "Advanced mentorship toward Ijazah with rigor on sanad, articulation and consistency across surahs.",
        "description": (
            "One-on-one sessions with certified instructors. Strict recitation standards and memorization polishing to prepare for Ijazah."
        ),
    },
    {
        "title": "Arabic Grammar (Nahw & Sarf) Basics",
        "price": "49",
        "lessons_count": 32,
        "image_url": "https://images.unsplash.com/photo-1483721310020-03333e577078?w=1600&q=80&auto=format&fit=crop",
        "overview": "A clear introduction to Nahw (syntax) and Sarf (morphology) to decode Quranic sentences.",
        "description": (
            "Learn cases, i'rab, verb forms and noun patterns with Quran-based examples and targeted exercises."
        ),
    },
]


def download_and_fit_image(url: str, target_w=1280, target_h=720) -> ContentFile:
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content)).convert('RGB')
    # center-crop to aspect 16:9 then resize
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        # wider than target → crop width
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    elif src_ratio < target_ratio:
        # taller than target → crop height
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))
    img = img.resize((target_w, target_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    buf.seek(0)
    return ContentFile(buf.read(), name=f"course_{timezone.now().timestamp()}.jpg")


class Command(BaseCommand):
    help = "Seed professionally curated Quran courses with high-quality images"

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete existing demo courses before seeding')

    def handle(self, *args, **options):
        # Ensure at least one instructor exists
        instructor = Instructor.objects.first()
        if instructor is None:
            instructor = Instructor.objects.create(
                name="Ustadh Ahmad",
                title="Senior Quran Instructor",
                bio="Certified in Tajweed and Qira'at with 10+ years of online teaching experience.",
                email=f"ustadh{int(timezone.now().timestamp())}@example.com",
                password='changeme123',
                is_active=True,
            )

        if options.get('reset'):
            Course.objects.all().delete()

        created = 0
        for data in CURATED_COURSES:
            title = data['title']
            if Course.objects.filter(title=title).exists():
                continue
            image_file = download_and_fit_image(data['image_url'])
            course = Course(
                title=title,
                description=data['description'],
                overview=data['overview'],
                lessons_count=data['lessons_count'],
                price=str(data['price']),
                instructor=instructor,
                is_trial_available=True,
                trial_days=3,
            )
            course.image.save(image_file.name, image_file, save=True)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} curated courses."))


