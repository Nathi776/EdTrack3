from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FaceEncoding",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("encoding", models.JSONField(help_text="Face embedding vector (length 128).")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("student", models.OneToOneField(help_text="Student profile linked to this face encoding.", on_delete=django.db.models.deletion.CASCADE, related_name="face_encoding", to="webapp.student")),
            ],
        ),
    ]
