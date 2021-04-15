from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from main.models import BaseUser, Meeting, Compliance, ComplianceOption, Region, Organization, MeetingTopic


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseUser
        fields = [
            'id', 'username', "password", 'phone', 'first_name', 'last_name'

        ]

    def create(self, validated_data):
        data = validated_data
        data['username'] = data.pop('phone')
        username = data.get('username')
        check_user = BaseUser.objects.filter(username=username).first()
        if check_user:
            raise ValidationError(
                {"Message": "User with this phone already exists", "code": 101})
        base_user = BaseUser.objects.create_user(
            phone=data['username'], **data)
        base_user.phone = data['username']

        return base_user

    # def update(self, instance, validated_data):
    #     pass


class BaseUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = ['id', 'username', 'first_name', 'last_name']


class IssueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingTopic
        fields = ['title']
        extra_kwargs = {
            'title': {
                'read_only': True,
            }
        }


class MeetingCreateSerializer(serializers.ModelSerializer):
    # title_uz = serializers.CharField(max_length=256, null=True, blank=True)
    # title_ru = serializers.CharField(max_length=256, null=True, blank=True)
    issues = IssueCreateSerializer(many=True, write_only=True)

    def create(self, validated_data):
        validated_data.pop('issues')
        return super().create(validated_data)

    class Meta:
        model = Meeting
        exclude = ['status', 'approved', 'count_approved', 'date_approved']
        extra_kwargs = {
            'issues': {
                'read_only': True,
            }
        }


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'title']


class ComplianceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        exclude = ['checked']


class MeetingSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(
        source='start_time', read_only=True, required=False)
    duration = serializers.SerializerMethodField(
        read_only=True, required=False)
    organization = serializers.CharField(
        source='organization.name', read_only=True, required=False)

    region = serializers.SerializerMethodField()
    def get_region(self, obj):
        if obj.organization:
            return RegionSerializer(obj.organization.region).data
        return 
    class Meta:
        model = Meeting
        exclude = ['count_approved', 'date_approved', 'created_at', 'updated_at']

    def get_duration(self, obj):
        duration = obj.end_time - obj.start_time
        duration = duration.total_seconds()
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        return {"hour": hours, "minutes": minutes}


class ComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = '__all__'
        read_only_fields = ['meeting', 'checked']

    def create(self, validated_data):
        meeting = Meeting.objects.filter(id=self.context['pk']).first()
        comp = Compliance.objects.create(meeting=meeting, **validated_data)
        return comp


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'id', 'name',
        ]


# class ParticipantTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Organization
#         fields = [
#             'id', 'name',
#         ]


class ComplianceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceOption
        fields = [
            'id', 'name',
        ]
