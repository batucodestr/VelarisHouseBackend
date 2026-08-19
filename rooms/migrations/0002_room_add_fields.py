from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="name",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="room",
            name="short_description",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
        migrations.AddField(
            model_name="room",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="room",
            name="size_sqm",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="room",
            name="bed_type",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="room",
            name="amenities",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="room",
            name="image_url",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="room",
            name="gallery",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="room",
            name="slug",
            field=models.SlugField(blank=True, default="", max_length=110),
        ),
    ]
