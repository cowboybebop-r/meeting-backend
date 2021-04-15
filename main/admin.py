from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m, IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm
from django.db import transaction, router
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import ugettext_lazy as _, gettext

from html import escape

from rest_auth.views import sensitive_post_parameters_m
from rest_framework.exceptions import PermissionDenied
# Register your models here.
from core import settings
from main.models import Organization, ComplianceOption, Meeting, MeetingTopic, Compliance, BaseUser, \
    Region, TelegramToken, AdminTelegramID  # ParticipantType

# admin.site.register(ParticipantType)
admin.site.register(ComplianceOption)

admin.site.register(TelegramToken)
admin.site.register(AdminTelegramID)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ['name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "region":
            queryset = Region.objects.all()
            if request.user.region and request.user.region_admin is True:
                queryset = queryset.filter(id=request.user.region.id)
            kwargs["queryset"] = queryset
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(OrganizationAdmin, self).get_queryset(request)
        if request.user.region and request.user.region_admin:
            return qs.filter(region=request.user.region.id)
        return qs


class MeetingTopicAdmin(admin.TabularInline):
    model = MeetingTopic


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'organization', 'start_time', 'end_time', 'organizer', 'approved', 'status']
    list_filter = ['status', 'organization']
    list_editable = ['approved']
    inlines = [MeetingTopicAdmin]
    def get_queryset(self, request):
        queryset = Meeting.objects.all()
        if request.user.is_superuser:
            return queryset
        elif request.user.region and request.user.region_admin:
            queryset = queryset.filter(organization__region=request.user.region.id)
            return queryset

        return queryset

@admin.register(Compliance)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['id', 'option', 'meeting', 'created_at', 'checked']


@admin.register(BaseUser)
class CustomUserAdmin(admin.ModelAdmin):
    add_form_template = 'admin/auth/user/add_form.html'
    list_display = ['id', 'username', ]
    change_user_password_template = None
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 'organization', 'phone', 'first_name', 'last_name',
                'is_approved'),
        }),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "region":
            queryset = Region.objects.all()
            if request.user.region and request.user.region_admin and not request.user.is_superuser:
                queryset = queryset.filter(id=request.user.region.id)
            kwargs["queryset"] = queryset

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        queryset = super(CustomUserAdmin, self).get_queryset(request)
        queryset = BaseUser.objects.all()
        if request.user.is_superuser:
            return queryset
        elif request.user.region and request.user.region_admin:
            queryset = queryset.filter(organization__region=request.user.region.id, is_superuser=False)
            return queryset

        return queryset

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
            Use special form during user creation
            """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_urls(self):
        return [
                   path(
                       '<id>/password/',
                       self.admin_site.admin_view(self.user_change_password),
                       name='auth_user_password_change',
                   ),
               ] + super().get_urls()

    def lookup_allowed(self, lookup, value):
        # Don't allow lookups involving passwords.
        return not lookup.startswith('password') and super().lookup_allowed(lookup, value)

    @sensitive_post_parameters_m
    @csrf_protect_m
    def add_view(self, request, form_url='', extra_context=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._add_view(request, form_url, extra_context)

    def _add_view(self, request, form_url='', extra_context=None):
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super().add_view(request, form_url, extra_context)

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        user = self.get_object(request, unquote(id))
        if not self.has_change_permission(request, user):
            raise PermissionDenied
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = gettext('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse('%s:%s_%s_change' % (
                        self.admin_site.name,
                        user._meta.app_label,
                        user._meta.model_name,
                    ),
                            args=(user.pk,),
                            )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context,
        )

    def response_add(self, request, obj, post_url_continue=None):
        """
            Determine the HttpResponse for the add_view stage. It mostly defers to
            its superclass implementation but is customized because the User model
            has a slightly different workflow.
            """
        if '_addanother' not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST = request.POST.copy()
            request.POST['_continue'] = 1
        return super().response_add(request, obj, post_url_continue)
