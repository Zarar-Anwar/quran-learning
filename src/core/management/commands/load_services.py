from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from urllib.request import urlopen
import os

from src.core.models import Service


class Command(BaseCommand):
    help = 'Load default services into the Service model'

    def handle(self, *args, **kwargs):
        services = [
            {
                "title": "Online Quran",
                "subtitle": "Classes",
                "description": "There are many variations of passages of lorem ipsum available lorem ipsum dolor sit amet",
                "icon_class": "flaticon-quran-1",
                "icon_file": "service-1.png",
            },
            {
                "title": "Online Islamic",
                "subtitle": "Classes",
                "description": "There are many variations of passages of lorem ipsum available lorem ipsum dolor sit amet",
                "icon_class": "flaticon-pray",
                "icon_file": "service-1.png",
            },
            {
                "title": "Expert Quran",
                "subtitle": "Tutor",
                "description": "There are many variations of passages of lorem ipsum available lorem ipsum dolor sit amet",
                "icon_class": "flaticon-quran-2",
                "icon_file": "service-1.png",
            },
            {
                "title": "Quranic Junior",
                "subtitle": "Al-Hafiz",
                "description": "There are many variations of passages of lorem ipsum available lorem ipsum dolor sit amet",
                "icon_class": "flaticon-quran-5",
                "icon_file": "service-1.png",
            },
            {
                "title": "Quran",
                "subtitle": "Translation",
                "description": "There are many variations of passages of lorem ipsum available lorem ipsum dolor sit amet",
                "icon_class": "flaticon-quran-4",
                "icon_file": "service-1.png",
            },
            {
                "title": "Islamic Studies For",
                "subtitle": "Kids Course",
                "description": "There are many variations of passages of lorem ipsum available lorem ipsum dolor sit amet",
                "icon_class": "flaticon-boy",
                "icon_file": "service-1.png",
            },
        ]

        base_url = 'http://localhost:8000/static/assets/images/icons/'  # replace with actual domain in production

        for s in services:
            if not Service.objects.filter(title=s["title"], subtitle=s["subtitle"]).exists():
                service = Service(
                    title=s["title"],
                    subtitle=s["subtitle"],
                    description=s["description"],
                    icon_class=s["icon_class"],
                )
                image_url = base_url + s["icon_file"]
                image_content = ContentFile(urlopen(image_url).read())
                service.big_icon.save(s["icon_file"], image_content, save=True)
                self.stdout.write(self.style.SUCCESS(f'Added service: {service.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Service already exists: {s["title"]}'))
