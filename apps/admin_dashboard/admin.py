"""Django admin configuration"""
from django.contrib import admin
from apps.analytics.models import AnalyticsEvent
from apps.authentication.models import User
from apps.companies.models import Company
from apps.compliance.models import ConsentType, PolicyVersion, UserConsent, UserPolicyAcceptance
from apps.notifications.models import ContactMessage, Notification
from apps.subscriptions.models import Invoice, PaymentMethod, Subscription
from apps.trials.models import FavoriteTrial, Industry, Trial, UserIndustry


# Custom admin classes
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'user_type', 'tier', 'is_active', 'email_verified', 'date_joined')
    list_filter = ('user_type', 'tier', 'is_active', 'email_verified')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'phone', 'website', 'created_at')
    search_fields = ('name', 'user__username', 'user__email')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Trial)
class TrialAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'industry', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'is_featured', 'industry')
    search_fields = ('title', 'description', 'company__name')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('company', 'industry')


@admin.register(FavoriteTrial)
class FavoriteTrialAdmin(admin.ModelAdmin):
    list_display = ('user', 'trial', 'created_at')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'trial')


@admin.register(UserIndustry)
class UserIndustryAdmin(admin.ModelAdmin):
    list_display = ('user', 'industry', 'created_at')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'industry')


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'trial', 'user', 'timestamp')
    list_filter = ('event_type',)
    ordering = ('-timestamp',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'trial')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    ordering = ('-created_at',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('company', 'provider', 'card_last4', 'card_brand', 'is_default', 'created_at')
    list_filter = ('provider', 'is_default')
    search_fields = ('company__name', 'card_last4')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('company')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company', 'trial', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('company__name', 'trial__title')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('company', 'trial')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'created_at')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('subscription')


@admin.register(ConsentType)
class ConsentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_required', 'created_at')
    list_filter = ('category', 'is_required')
    ordering = ('name',)


@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = ('user', 'consent_type', 'given', 'version', 'created_at')
    list_filter = ('given', 'consent_type')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'consent_type')


@admin.register(PolicyVersion)
class PolicyVersionAdmin(admin.ModelAdmin):
    list_display = ('policy_type', 'version', 'effective_date', 'created_at')
    list_filter = ('policy_type',)
    ordering = ('-effective_date',)


@admin.register(UserPolicyAcceptance)
class UserPolicyAcceptanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'policy_version', 'accepted_at')
    ordering = ('-accepted_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'policy_version')