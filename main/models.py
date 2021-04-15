import requests
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from main.manager import UserManager


class SingletonModel(models.Model):
    """Singleton Django Model"""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Save object to the database. Removes all other entries if there
        are any.
        """
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Load object from the database. Failing that, create a new empty
        (default) instance of the object and return it (without saving it
        to the database).
        """

        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


class BaseModel(models.Model):
    created_at = models.DateTimeField(_('Kiritilgan sana'), auto_now_add=True)
    updated_at = models.DateTimeField(_('O\'zgartirilgan sana'), auto_now=True)

    class Meta:
        abstract = True


class Region(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title}" or f'{self.pk}'


class Organization(BaseModel):
    name = models.CharField(max_length=132)
    status = models.BooleanField(default=False)
    region = models.ForeignKey(Region, verbose_name=_("Region"), null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Tashkilot'
        verbose_name_plural = 'Tashkilotlar'

    def __str__(self):
        return f"{self.name}"


class BaseUser(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("Bu foydalanuvchi nomi allaqachon mavjud."),
        },
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                     verbose_name=_('Tashkilot'), null=True, blank=True)

    phone_regex = RegexValidator(regex=r'^\d{9}$', message=_("13-ta raqamgacha ruxsat berilgan."))
    first_name = models.CharField(_('Ism'), max_length=128, blank=True)
    last_name = models.CharField(_('Familiyasi'), max_length=128, blank=True)
    email = models.EmailField(_('Email'), blank=True, null=True)
    active = models.BooleanField(_('Aktiv'), default=True),
    is_approved = models.BooleanField(_('Tasdiqlangan'), default=False)
    date_joined = models.DateTimeField(_('Ro\'yxatdan o\'tgan sana'), default=timezone.now)
    last_login = models.DateTimeField(_('Oxirgi aktiv holati'), null=True, blank=True, default=timezone.now)
    phone = models.CharField(_('Telefon raqam'), max_length=60, validators=[phone_regex], null=True, blank=True)
    region_admin = models.BooleanField(_('Viloyat admin'), default=False)
    region = models.ForeignKey(Region, verbose_name=_("Region"), null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(_('Kiritilgan sana'), auto_now_add=True)
    updated_at = models.DateTimeField(_('O\'zgartirilgan sana'), auto_now=True)
    objects = UserManager()

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'


# class ParticipantType(BaseModel):
#     name = models.CharField(max_length=132)

#     class Meta:
#         verbose_name = 'Ishtirokchi turi'
#         verbose_name_plural = 'Ishtirokchi turlari'

#     def __str__(self):
#         return f"{self.name}"


class ComplianceOption(BaseModel):
    name = models.CharField(max_length=132)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Shikoyat mavzusi'
        verbose_name_plural = 'Shikoyat mavzusi'
        ordering = ['order']

    def __str__(self):
        return f"{self.name}"


class Meeting(BaseModel):
    STATUS = (
        (1, _('Reja qilingan')),
        (2, _('Jarayonda')),
        (3, _('Yakunlangan')),
        (4, _('Bekor qilingan'))
    )
    title = models.CharField(_('Majlis mavzusi'), max_length=256, null=True, blank=True)
    organization = models.ForeignKey(Organization, verbose_name=_("Tashkilot"), null=True, blank=True,
                                     on_delete=models.SET_NULL)
    start_time = models.DateTimeField(_('Boshlanish Vaqti'), null=True, blank=True)
    end_time = models.DateTimeField(_('Tugash Vaqti'), null=True, blank=True)
    organizer = models.CharField(_('Tashkilotchi'), max_length=128, null=True)
    organizer_position = models.CharField(_('Tashkilotchi lavozimi'), max_length=128, null=True)
    status = models.PositiveSmallIntegerField(_("Holati"), choices=STATUS, default=1)
    approved = models.BooleanField(_('Tasdiqlangan'), default=False)
    participant_type = models.CharField(_('Ishtirokchilar turi'), max_length=128, null=True)
    participant_number = models.PositiveIntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    count_approved = models.BooleanField(_('Ishtirokchi soni tasdiqlandi'), default=False)
    date_approved = models.BooleanField(_('sana tasdiqlandi'), default=False)

    class Meta:
        verbose_name = 'Majlis'
        verbose_name_plural = 'Majlislar'

    def __str__(self):
        return f"{self.title}" or f'{self.pk}'

    @property
    def get_approved(self):
        if self.approved == True:
            return 'Ha'
        else:
            return 'Yoq'

    @property
    def get_count_approved(self):
        if self.count_approved == True:
            return 'Ha'
        else:
            return 'Yoq'

    def get_time_diff(self):
        if self.start_time and self.end_time:
            timediff = self.end_time - self.start_time
            return timediff.total_seconds()


class MeetingTopic(BaseModel):
    title = models.CharField(_('Majlis mavzusi'), max_length=256)
    meeting = models.ForeignKey(Meeting, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Majlis"))

    class Meta:
        verbose_name = 'Majlis mavzusi'
        verbose_name_plural = 'Majlis mavzulari'

    def __str__(self):
        return f"{self.title}" or f'{self.pk}'


class Compliance(BaseModel):
    meeting = models.ForeignKey(Meeting, null=True, blank=True, on_delete=models.SET_NULL)
    option = models.ForeignKey(ComplianceOption, null=True, blank=True, on_delete=models.SET_NULL)
    comment = models.TextField(null=True, blank=True)
    show_contact = models.BooleanField(default=False)
    phone_number = models.CharField(_('Telefon raqami'), max_length=15, null=True, blank=True)
    checked = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Shikoyat'
        verbose_name_plural = 'Shikoyatlar'

    def __str__(self):
        return f'{self.pk}'


class TelegramToken(SingletonModel):
    token = models.CharField('Telegram Token', max_length=256)

    def __str__(self):
        return self.token


class AdminTelegramID(models.Model):
    chat_id = models.PositiveIntegerField()
    full_name = models.CharField('Adminni ismi', max_length=256)

    def __str__(self):
        return self.full_name


@receiver(post_save, sender=Meeting)
def send_message(instance, **kwargs):
    token = TelegramToken.load()
    method = 'sendMessage'
    host = 'http://127.0.0.1:8000/admin/main/meeting/'
    admins = AdminTelegramID.objects.all()
    data = 'Majlis mavzusi: *{title}*\n' \
           'Tashkilot: *{organization}*\n' \
           'Boshlanish Vaqti: *{start_time}*\n' \
           'Tugash Vaqti: *{end_time}*\n' \
           'Tashkilotchi: *{organizer}*\n' \
           'Tashkilotchi lavozimi: *{organizer_position}*\n' \
           'Holati: *{status}*\n' \
           'Tasdiqlangan: *{approved}*\n' \
           'Ishtirokchilar turi: *{participant_type}*\n' \
           'Ishtirokchi soni tasdiqland: *{count_approved}*\n\n' \
           '{link}'.format(
                title=instance.title,
                organization=instance.organization,
                start_time=instance.start_time,
                end_time=instance.end_time,
                organizer=instance.organizer,
                organizer_position=instance.organizer_position,
                status=instance.status,
                approved=instance.get_approved,
                participant_type=instance.participant_type,
                count_approved=instance.get_count_approved,
                link=host + str(instance.id),
            )
    api_url = 'https://api.telegram.org/bot{token}/{method}?chat_id={chat_id}&text={data}&parse_mode=Markdown'
    for admin in admins:
        requests.post(api_url.format(token=token, method=method, chat_id=admin.chat_id, data=data)).json()
