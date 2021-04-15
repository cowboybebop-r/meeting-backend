from django.shortcuts import render

# Create your views here.
from rest_auth.views import LoginView
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import BaseUser, MeetingTopic, Meeting, Compliance, ComplianceOption, Organization,  \
    Region
from main.pagination import CustomPagination
from main.serializers import MeetingCreateSerializer, MeetingSerializer, ComplianceSerializer, RegionSerializer, \
    ComplianceCreateSerializer, ComplianceOptionSerializer, OrganizationSerializer,  \
    BaseUserSerializer, BaseUserProfileSerializer
# ParticipantType ParticipantTypeSerializer


class UserLoginView(LoginView):

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()

    def get_response(self):
        original_response = super().get_response()
        token = Token.objects.get(key=original_response.data['key'])
        user = BaseUser.objects.get(id=token.user.id)
        data = {
            'message': 'Successfully logged in',
            'status': 200,
            'token': token.key
        }
        original_response.data.update(data)
        return Response(data)


# LOGOUT
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaseUserProfileSerializer

    def get(self, request, format=None):
        user = self.request.user
        data = self.serializer_class(user).data
        return Response(data)


class MeetingCreateView(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Meeting.objects.order_by('-created_at')
    serializer_class = MeetingCreateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = MeetingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meeting = serializer.save()
        meeting.organization = self.request.user.organization
        meeting.save()

        try:
            issue_list = self.request.data.get('issues')
        except:
            issue_list = None

        if issue_list:
            for item in issue_list:
                MeetingTopic.objects.create(title=item.get('title', None),
                                            meeting=meeting)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ComplianceCreateView(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Compliance.objects.order_by(
        '-created_at')
    serializer_class = ComplianceCreateSerializer
    # permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request):
        serializer = ComplianceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        compliance = serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class MeetingListView(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Meeting.objects.filter(approved=True)
    serializer_class = MeetingSerializer
    pagination_class = CustomPagination
    http_method_names = ['get']

    def get_queryset(self):
        queryset = self.queryset
        query_params = self.request.query_params
        meeting_status = query_params.get('status', None)
        organization = query_params.get('organization', None)
        region = query_params.get('region', None)
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')
        search = self.request.query_params.get('search')

        if meeting_status is not None:
            queryset = queryset.filter(status=meeting_status)

        if search:
            queryset = queryset.filter(title__icontains=search)

        if organization is not None:
            queryset = queryset.filter(organization_id=organization)

        if region is not None:
            queryset = queryset.filter(organization__region_id=region)

        if region is not None:
            queryset = queryset.filter(organization__region_id=region)

        if start_time is not None and end_time is not None:
            queryset = queryset.filter(
                start_time__gte=start_time, end_time__lte=end_time)

        return queryset


class MeetingMyListView(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Meeting.objects.order_by('-created_at')
    permission_classes = [IsAuthenticated]
    serializer_class = MeetingSerializer
    pagination_class = CustomPagination
    http_method_names = ['get']

    def get_queryset(self):
        queryset = self.queryset.filter(
            organization__baseuser=self.request.user)
        query_params = self.request.query_params
        meeting_status = query_params.get('status', None)
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')

        if meeting_status is not None:
            queryset = queryset.filter(status=meeting_status)

        if start_time is not None and end_time is not None:
            queryset = queryset.filter(
                start_time__gte=start_time, end_time__lte=end_time)

        return queryset


class MeetingListByRegionView(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Meeting.objects.filter(approved=True)
    serializer_class = MeetingSerializer
    pagination_class = CustomPagination
    http_method_names = ['get']

    def list(self, request):
        region = self.request.query_params.get('region')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')
        queryset = self.queryset.filter(approved=True).exclude(status=1)
        if region:
            organizations = Organization.objects.filter(region=region)
            queryset = queryset.filter(
                organization_id__in=organizations.values_list('id'),)
        if start_time:
            queryset = queryset.filter(
                start_time__gte=start_time, end_time__gt=start_time,)
        if end_time:
            queryset = queryset.filter(
                end_time__lte=end_time, start_time__lte=end_time,)
        meeting_count = queryset.count()
        total_number = queryset.extra(
            select={'total_number': 'SUM(main_meeting.participant_number)'}).values('total_number')[0]['total_number']
        total_time = queryset.extra(
            select={'total_diff': 'SUM(main_meeting.end_time - main_meeting.start_time)'}).values('total_diff')[0][
            'total_diff']
        data = {
            'meeting_count': meeting_count,
            'total_time': total_time,
            'total_number': total_number,

        }

        return Response(data, status=status.HTTP_200_OK)


class MeetingCommentView(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Compliance.objects.all()
    serializer_class = ComplianceSerializer

    def post(self, request, pk=None, ):
        serializer = ComplianceSerializer(data=request.data, context={
            'request': self.request, 'pk': pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrganizationView(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Organization.objects.filter(status=True).order_by(
        '-id')
    serializer_class = OrganizationSerializer
    pagination_class = CustomPagination
    http_method_names = ['get']

    def list(self, request):
        query = self.request.query_params.get('query')
        instance = self.queryset
        serializer = self.serializer_class
        if query:
            instance = self.queryset.filter(name__icontains=query)

        payload = {
            'title': 'Organizations',
            'data': serializer(instance, many=True).data
        }
        return Response(payload)


# class ParticipantTypeView(viewsets.ModelViewSet, generics.ListAPIView):
#     queryset = ParticipantType.objects.order_by(
#         '-id')
#     serializer_class = ParticipantTypeSerializer
#     pagination_class = None
#     http_method_names = ['get']

#     def get_serializer_class(self):
#         if self.action == 'retrieve':
#             return ParticipantTypeSerializer
#         return ParticipantTypeSerializer


class RegionView(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    pagination_class = None
    http_method_names = ['get']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RegionSerializer
        return RegionSerializer


class ComplianceOptionListView(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = ComplianceOption.objects.order_by(
        '-order')
    serializer_class = ComplianceOptionSerializer
    pagination_class = None
    http_method_names = ['get']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ComplianceOptionSerializer
        return ComplianceOptionSerializer
