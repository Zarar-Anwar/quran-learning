from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from faker import Faker
import io
from PIL import Image, ImageDraw

from src.services.courses.models import Course, Instructor


class Command(BaseCommand):
    help = "Seed random instructors and courses for testing"

    def add_arguments(self, parser):
        parser.add_argument('--courses', type=int, default=8, help='Number of courses to create')
        parser.add_argument('--instructors', type=int, default=3, help='Number of instructors to create')

    def handle(self, *args, **options):
        fake = Faker()

        # Ensure instructors
        instructors = list(Instructor.objects.all())
        needed = max(0, options['instructors'] - len(instructors))
        for _ in range(needed):
            name = fake.name()
            inst = Instructor.objects.create(
                name=name,
                title=fake.job(),
                bio=fake.paragraph(nb_sentences=3),
                email=fake.unique.email(),
                password='changeme123',
                is_active=True,
            )
            instructors.append(inst)

        # Helper to generate placeholder image (1280x720)
        def generate_placeholder(title: str) -> ContentFile:
            width, height = 1280, 720
            img = Image.new('RGB', (width, height), color=(40, 167, 69))
            draw = ImageDraw.Draw(img)
            text = (title[:22] + '...') if len(title) > 25 else title
            # center text
            tw, th = draw.textlength(text), 20
            draw.text(((width - tw) / 2, (height - th) / 2), text, fill=(255, 255, 255))
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=85)
            buf.seek(0)
            return ContentFile(buf.read(), name=f"course_{timezone.now().timestamp()}.jpg")

        created = 0
        for i in range(options['courses']):
            title = f"{fake.word().capitalize()} Quran Course {fake.random_int(1, 99)}"
            description = fake.paragraph(nb_sentences=5)
            overview = fake.paragraph(nb_sentences=8)
            lessons_count = fake.random_int(min=8, max=40)
            price = fake.random_element(elements=("Free", "19.99", "29.00", "49/mo", "99 one-time"))
            instructor = fake.random_element(elements=instructors) if instructors else None

            course = Course(
                title=title,
                description=description,
                overview=overview,
                lessons_count=lessons_count,
                price=str(price),
                instructor=instructor,
                is_trial_available=fake.boolean(chance_of_getting_true=60),
                trial_days=fake.random_int(min=1, max=7)
            )
            image_file = generate_placeholder(title)
            course.image.save(image_file.name, image_file, save=True)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} courses and {len(instructors)} instructors."))


