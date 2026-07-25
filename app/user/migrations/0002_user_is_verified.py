from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("user", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
    ]
