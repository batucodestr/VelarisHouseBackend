from django.db import migrations


ROOMS = [
    dict(
        room_number=101, keybox_code="1011", room_type="suite", price="4500.00",
        capacity=2, is_active=True, name="Suit 01",
        short_description="Özel tasarım ahşap paneller, geniş pencereler ve saf keten dokunuşlar.",
        description=(
            "En ince detayına kadar düşünülmüş Suit 01, geniş yaşam alanı ve özel "
            "tasarım mobilyalarıyla Velaris House deneyiminin zirvesini sunar. Ahşap "
            "panellerin sıcaklığı ve saf keten çarşafların rahatlığıyla zamanın "
            "yavaşladığını hissedeceksiniz."
        ),
        size_sqm=45, bed_type="King Size",
        amenities=["wifi", "ac", "minibar", "room_service", "safe", "bath"],
    ),
    dict(
        room_number=102, keybox_code="1022", room_type="double", price="2800.00",
        capacity=2, is_active=True, name="Avlu Oda",
        short_description="İç avlunun dinginliğine açılan, huzur dolu bir sığınak.",
        description=(
            "Tarihi yapının kalbindeki iç avluya bakan bu oda, günün her saati farklı "
            "bir ışık oyununa sahne olur. Şehrin gürültüsünden uzak, tamamen sessizlik "
            "ve huzur arayan misafirlerimiz için idealdir."
        ),
        size_sqm=28, bed_type="Queen Size",
        amenities=["wifi", "ac", "minibar", "safe", "view"],
    ),
    dict(
        room_number=103, keybox_code="1033", room_type="suite", price="5500.00",
        capacity=3, is_active=True, name="Teraslı Suit",
        short_description="Özel terasınızda akşam üstü kahvenizi yudumlayacağınız benzersiz bir alan.",
        description=(
            "Kendinize ait özel terasıyla öne çıkan bu suit, iç mekanın lüksünü dış "
            "mekanın ferahlığıyla birleştirir. Gün batımında terasınızda zaman "
            "geçirmek, Velaris House deneyiminin vazgeçilmez bir parçasıdır."
        ),
        size_sqm=55, bed_type="King Size + Sofa",
        amenities=["wifi", "ac", "minibar", "room_service", "safe", "bath", "terrace", "view"],
    ),
    dict(
        room_number=104, keybox_code="1044", room_type="double", price="3200.00",
        capacity=2, is_active=True, name="Klasik Oda",
        short_description="Yüksek tavanlar, kadife detaylar ve zamansız bir zarafet.",
        description=(
            "Tarihi binanın orijinal dokusunu en iyi yansıtan Klasik Oda, yüksek "
            "tavanları ve özenle seçilmiş antika detaylarıyla misafirlerini geçmişe "
            "doğru şık bir yolculuğa çıkarır."
        ),
        size_sqm=32, bed_type="Queen Size",
        amenities=["wifi", "ac", "minibar", "safe", "tv"],
    ),
    dict(
        room_number=105, keybox_code="1055", room_type="double", price="3500.00",
        capacity=2, is_active=True, name="Çatı Katı",
        short_description="Açık ahşap kirişlerin altında samimi, sıcak ve romantik bir atmosfer.",
        description=(
            "Evin en üst katında, eğimli tavanı ve orijinal ahşap kirişleriyle Çatı "
            "Katı odası, sıcak ve koza gibi saran bir atmosfere sahiptir. Romantik "
            "kaçamaklar için en çok tercih edilen odamızdır."
        ),
        size_sqm=35, bed_type="King Size",
        amenities=["wifi", "ac", "minibar", "safe", "bath", "view"],
    ),
    dict(
        room_number=106, keybox_code="1066", room_type="suite", price="6200.00",
        capacity=4, is_active=True, name="Geniş Suit",
        short_description="Büyük pencerelerden süzülen ışık ve rakipsiz bir ferahlık hissi.",
        description=(
            "Geniş aileler veya ekstra alana ihtiyaç duyan misafirlerimiz için "
            "tasarlanmış Geniş Suit, oturma ve yatak bölümlerinin akıcı bir şekilde "
            "birleştiği, ferah ve aydınlık bir yaşam alanı sunar."
        ),
        size_sqm=65, bed_type="King Size + 2 Single Beds",
        amenities=["wifi", "ac", "minibar", "room_service", "safe", "bath", "tv", "view"],
    ),
]


def seed_rooms(apps, schema_editor):
    Room = apps.get_model("rooms", "Room")
    from django.utils.text import slugify

    for data in ROOMS:
        if Room.objects.filter(room_number=data["room_number"]).exists():
            continue
        room = Room(**data, gallery=[], image_url="")
        room.slug = slugify(room.name)
        room.save()


def unseed_rooms(apps, schema_editor):
    Room = apps.get_model("rooms", "Room")
    Room.objects.filter(
        room_number__in=[r["room_number"] for r in ROOMS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0004_room_slug_unique"),
    ]

    operations = [
        migrations.RunPython(seed_rooms, unseed_rooms),
    ]
