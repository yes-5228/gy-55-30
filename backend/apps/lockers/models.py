from django.db import models


class LockerCell(models.Model):
    class Size(models.TextChoices):
        SMALL = "small", "小"
        MEDIUM = "medium", "中"
        LARGE = "large", "大"

    class Status(models.TextChoices):
        EMPTY = "empty", "空闲"
        OCCUPIED = "occupied", "已占用"
        OPEN = "open", "已开门"
        MAINTENANCE = "maintenance", "维护中"

    code = models.CharField(max_length=20, unique=True)
    zone = models.CharField(max_length=30, default="A区")
    size = models.CharField(max_length=20, choices=Size.choices, default=Size.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EMPTY)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, default=24)
    last_opened_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["zone", "code"]

    def __str__(self):
        return f"{self.zone}-{self.code}"


class ReleaseRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "待审批"
        APPROVED = "approved", "已通过"
        REJECTED = "rejected", "已拒绝"

    locker_cell = models.ForeignKey(
        LockerCell,
        on_delete=models.CASCADE,
        related_name="release_requests",
    )
    reason = models.TextField()
    applicant = models.CharField(max_length=40, default="客服")
    reviewer = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    review_remark = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"释放申请 {self.locker_cell.code} {self.get_status_display()}"
