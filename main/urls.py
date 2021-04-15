from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()

# INTERNAL MODULES
from . import views

router.register(r'meeting/create', views.MeetingCreateView, basename='meeting_create-api')
router.register(r'meeting/list', views.MeetingListView, basename='meeting_list-api')
router.register(r'meeting/mylist', views.MeetingMyListView, basename='meeting_list-api')
router.register(r'meeting/list/<int:pk>/comment', views.MeetingCommentView, basename='meeting_comment-api')
router.register(r'meeting/region', views.MeetingListByRegionView, basename='meeting_list-region-api')

router.register(r'compliance/create', views.ComplianceCreateView, basename='compliance_create-api')
router.register(r'compliance-option', views.ComplianceOptionListView, basename='compliance-option-api')

router.register(r'organization', views.OrganizationView, basename='organization-api')

# router.register(r'participanttype', views.ParticipantTypeView, basename='participanttype-api')
router.register(r'regions', views.RegionView, basename='regions-api')

urlpatterns = [
    path('', include(router.urls)),
    path('account/login/', views.UserLoginView.as_view(), {}, name='login'),
    path('account/logout/', views.UserLogoutView.as_view(), {}, name='logout'),
    path('account/profile/', views.UserProfileView.as_view(), {}, name='profile'),
]

# path('meeting/create/', views.MeetingCreateView.as_view(), name='meeting_create'),
# path('meeting/list/', views.MeetingListView.as_view(), name='meeting_list'),
# path('meeting/list/<int:pk>/comment/', views.MeetingCommentView.as_view(), name='meeting_comment'),
