from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0003_room_populate_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="slug",
            field=models.SlugField(blank=True, max_length=110, unique=True),
        ),
    ]
