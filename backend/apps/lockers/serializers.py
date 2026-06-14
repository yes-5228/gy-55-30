from rest_framework import serializers

from .models import LockerCell, ReleaseRequest


class LockerCellSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    size_label = serializers.CharField(source="get_size_display", read_only=True)

    class Meta:
        model = LockerCell
        fields = [
            "id",
            "code",
            "zone",
            "size",
            "size_label",
            "status",
            "status_label",
            "temperature",
            "last_opened_at",
            "updated_at",
        ]


class ReleaseRequestSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    cell_code = serializers.CharField(source="locker_cell.code", read_only=True)
    cell_zone = serializers.CharField(source="locker_cell.zone", read_only=True)
    cell_status = serializers.CharField(source="locker_cell.status", read_only=True)

    class Meta:
        model = ReleaseRequest
        fields = [
            "id",
            "locker_cell",
            "cell_code",
            "cell_zone",
            "cell_status",
            "reason",
            "applicant",
            "reviewer",
            "status",
            "status_label",
            "review_remark",
            "created_at",
            "reviewed_at",
        ]
        read_only_fields = ["reviewer", "status", "review_remark", "reviewed_at"]


class ReleaseRequestApplySerializer(serializers.Serializer):
    locker_cell = serializers.IntegerField()
    reason = serializers.CharField()


class ReleaseRequestReviewSerializer(serializers.Serializer):
    reviewer = serializers.CharField(default="管理员")
    review_remark = serializers.CharField(required=False, default="")
