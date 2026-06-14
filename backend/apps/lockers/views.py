from django.db.models import Count
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import LockerCell, ReleaseRequest
from .serializers import (
    LockerCellSerializer,
    ReleaseRequestApplySerializer,
    ReleaseRequestReviewSerializer,
    ReleaseRequestSerializer,
)


class LockerCellViewSet(viewsets.ModelViewSet):
    queryset = LockerCell.objects.all()
    serializer_class = LockerCellSerializer

    @action(detail=False, methods=["get"])
    def summary(self, request):
        total = LockerCell.objects.count()
        by_status = {
            item["status"]: item["count"]
            for item in LockerCell.objects.values("status").annotate(count=Count("id"))
        }
        return Response(
            {
                "total": total,
                "empty": by_status.get(LockerCell.Status.EMPTY, 0),
                "occupied": by_status.get(LockerCell.Status.OCCUPIED, 0),
                "open": by_status.get(LockerCell.Status.OPEN, 0),
                "maintenance": by_status.get(LockerCell.Status.MAINTENANCE, 0),
            }
        )

    @action(detail=True, methods=["post"])
    def mark_maintenance(self, request, pk=None):
        cell = self.get_object()
        cell.status = LockerCell.Status.MAINTENANCE
        cell.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(cell).data)

    @action(detail=True, methods=["post"])
    def reset(self, request, pk=None):
        cell = self.get_object()
        cell.status = LockerCell.Status.EMPTY
        cell.last_opened_at = timezone.now()
        cell.save(update_fields=["status", "last_opened_at", "updated_at"])
        return Response(self.get_serializer(cell).data)


class ReleaseRequestViewSet(viewsets.ModelViewSet):
    queryset = ReleaseRequest.objects.select_related("locker_cell").all()
    serializer_class = ReleaseRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = ReleaseRequestApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cell_id = serializer.validated_data["locker_cell"]
        reason = serializer.validated_data["reason"]
        try:
            cell = LockerCell.objects.get(pk=cell_id)
        except LockerCell.DoesNotExist:
            return Response({"detail": "柜格不存在"}, status=404)
        if cell.status == LockerCell.Status.EMPTY:
            return Response({"detail": "该柜格已是空闲状态，无需释放"}, status=400)
        rr = ReleaseRequest.objects.create(
            locker_cell=cell,
            reason=reason,
            applicant=request.data.get("applicant", "客服"),
        )
        return Response(ReleaseRequestSerializer(rr).data, status=201)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        rr = self.get_object()
        if rr.status != ReleaseRequest.Status.PENDING:
            return Response({"detail": "只能审批待审批的申请"}, status=400)
        serializer = ReleaseRequestReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rr.status = ReleaseRequest.Status.APPROVED
        rr.reviewer = serializer.validated_data["reviewer"]
        rr.review_remark = serializer.validated_data.get("review_remark", "")
        rr.reviewed_at = timezone.now()
        rr.save()
        cell = rr.locker_cell
        cell.status = LockerCell.Status.EMPTY
        cell.last_opened_at = timezone.now()
        cell.save(update_fields=["status", "last_opened_at", "updated_at"])
        return Response(ReleaseRequestSerializer(rr).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        rr = self.get_object()
        if rr.status != ReleaseRequest.Status.PENDING:
            return Response({"detail": "只能审批待审批的申请"}, status=400)
        serializer = ReleaseRequestReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rr.status = ReleaseRequest.Status.REJECTED
        rr.reviewer = serializer.validated_data["reviewer"]
        rr.review_remark = serializer.validated_data.get("review_remark", "")
        rr.reviewed_at = timezone.now()
        rr.save()
        return Response(ReleaseRequestSerializer(rr).data)
