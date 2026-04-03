from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_date_of_birth_user_email_verified_user_sex_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_emergency_user",
            field=models.BooleanField(
                default=False,
                help_text="Peut déclencher la procédure de purge d'urgence.",
            ),
        ),
    ]
