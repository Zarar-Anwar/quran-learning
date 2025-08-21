from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone

import io
from PIL import Image, ImageDraw

from src.core.models import Service


CURATED_SERVICES = [
    {
        "title": "Noorani Qaida",
        "subtitle": "Arabic Reading Basics",
        "description": "Master Arabic alphabets, harakaat, sukoon and joining to start reading the Quran correctly.",
        "icon_class": "flaticon-quran-1",
        "detail_page_url": "service-detail.html",
    },
    {
        "title": "Tajweed Rules",
        "subtitle": "Makharij & Sifaat",
        "description": "Learn articulation points, characteristics, madd, ikhfa, idgham and more with coached practice.",
        "icon_class": "flaticon-quran-3",
        "detail_page_url": "service-detail.html",
    },
    {
        "title": "Quran Memorization (Hifz)",
        "subtitle": "Personalized Plans",
        "description": "Structured sabaq, sabaqi and manzil cycles with weekly assessments to build strong memorization.",
        "icon_class": "flaticon-book",
        "detail_page_url": "service-detail.html",
    },
    {
        "title": "Quran Recitation for Kids",
        "subtitle": "Fun & Engaging",
        "description": "Child-friendly reading with short surah goals, rewards, and gentle coaching to build fluency.",
        "icon_class": "flaticon-reading",
        "detail_page_url": "service-detail.html",
    },
    {
        "title": "Arabic for Understanding",
        "subtitle": "Quranic Vocabulary",
        "description": "High‑frequency Quranic words and patterns to understand verses without translation.",
        "icon_class": "flaticon-dictionary",
        "detail_page_url": "service-detail.html",
    },
    {
        "title": "Tafsir Essentials",
        "subtitle": "Themes of the Quran",
        "description": "Explore Tawheed, Prophethood, Ethics and Hereafter with classical and contemporary Tafsir.",
        "icon_class": "flaticon-open-book",
        "detail_page_url": "service-detail.html",
    },
    {
        "title": "Islamic Studies",
        "subtitle": "Aqeedah • Fiqh • Seerah",
        "description": "Balanced curriculum covering belief, jurisprudence, prophetic biography and daily adab.",
        "icon_class": "flaticon-mosque",
        "detail_page_url": "service-detail.html",
    },
    {
        "title": "Ijazah Preparation",
        "subtitle": "Advanced Qira'at",
        "description": "Mentorship toward Ijazah with sanad focus, strict recitation standards and polishing.",
        "icon_class": "flaticon-certification",
        "detail_page_url": "service-detail.html",
    },
]


def generate_placeholder(title: str, width: int = 640, height: int = 640) -> ContentFile:
    """Create a simple square placeholder image for service big_icon."""
    img = Image.new('RGB', (width, height), color=(30, 136, 229))  # blue
    draw = ImageDraw.Draw(img)
    text = (title[:22] + '…') if len(title) > 22 else title
    # naive centering using textlength (no font metrics available)
    tw = draw.textlength(text)
    draw.text(((width - tw) / 2, height / 2 - 10), text, fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    ts = str(timezone.now().timestamp()).replace('.', '')
    return ContentFile(buf.read(), name=f"service_{ts}.png")


class Command(BaseCommand):
    help = "Seed 8 curated Quran/Madrasa services with icons and descriptions"

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete existing services before seeding')

    def handle(self, *args, **options):
        if options.get('reset'):
            Service.objects.all().delete()

        created = 0
        for data in CURATED_SERVICES:
            if Service.objects.filter(title=data['title']).exists():
                continue
            service = Service(
                title=data['title'],
                subtitle=data['subtitle'],
                description=data['description'],
                icon_class=data['icon_class'],
                detail_page_url=data['detail_page_url'],
            )
            img_file = generate_placeholder(data['title'])
            service.big_icon.save(img_file.name, img_file, save=True)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} services."))


