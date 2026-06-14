from rest_framework.routers import DefaultRouter

from .views import LockerCellViewSet, ReleaseRequestViewSet

router = DefaultRouter()
router.register("cells", LockerCellViewSet, basename="locker-cell")
router.register("release-requests", ReleaseRequestViewSet, basename="release-request")

urlpatterns = router.urls
