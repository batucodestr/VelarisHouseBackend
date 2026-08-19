from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Room = apps.get_model("rooms", "Room")
    used = set()
    for room in Room.objects.all():
        base = slugify(room.name) or f"room-{room.room_number}"
        slug = base
        i = 2
        while slug in used or Room.objects.exclude(pk=room.pk).filter(slug=slug).exists():
            slug = f"{base}-{i}"
            i += 1
        used.add(slug)
        room.slug = slug
        room.save(update_fields=["slug"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0002_room_add_fields"),
    ]

    operations = [
        migrations.RunPython(populate_slugs, noop),
    ]
