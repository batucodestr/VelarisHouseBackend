from django.db import models
from django.utils.text import slugify


class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ("single", "Single"),
        ("double", "Double"),
        ("suite", "Suite"),
    ]

    room_number = models.PositiveIntegerField(unique=True)

    keybox_code = models.CharField(max_length=4)

    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    capacity = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)

    name = models.CharField(max_length=100, blank=True, default="")

    slug = models.SlugField(max_length=110, unique=True, blank=True)

    short_description = models.CharField(max_length=300, blank=True, default="")

    description = models.TextField(blank=True, default="")

    size_sqm = models.PositiveIntegerField(default=0)

    bed_type = models.CharField(max_length=100, blank=True, default="")

    amenities = models.JSONField(default=list, blank=True)

    image_url = models.URLField(blank=True, default="")

    gallery = models.JSONField(default=list, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.name or f"room-{self.room_number}"
            candidate = slugify(base) or f"room-{self.room_number}"
            slug = candidate
            i = 2
            while Room.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{candidate}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Room {self.room_number}"
