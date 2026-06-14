from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("lockers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReleaseRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reason", models.TextField()),
                ("applicant", models.CharField(default="客服", max_length=40)),
                ("reviewer", models.CharField(blank=True, max_length=40)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "待审批"), ("approved", "已通过"), ("rejected", "已拒绝")],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("review_remark", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("locker_cell", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="release_requests", to="lockers.lockercell")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
