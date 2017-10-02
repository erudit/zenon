# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from erudit.models import Journal
from .models import InstitutionIPAddressRange
from .models import InstitutionReferer
from .models import JournalAccessSubscription
from .models import JournalAccessSubscriptionPeriod
from .models import JournalManagementPlan
from .models import JournalManagementSubscription
from .models import JournalManagementSubscriptionPeriod


class JournalAccessSubscriptionPeriodInline(admin.TabularInline):
    model = JournalAccessSubscriptionPeriod


class InstitutionRefererInline(admin.TabularInline):
    model = InstitutionReferer


class InstitutionIPAddressRangeAdmin(admin.ModelAdmin):
    search_fields = ('subscription__organisation__name',)


class SubscriptionTypeListFilter(admin.SimpleListFilter):
    title = _("Type d'abonnement")
    parameter_name = "subscription_type"

    def lookups(self, request, model_admin):
        return (
            ('individual', _('Abonnements individuels')),
            ('institution', _('Abonnements institutionnels'))
        )

    def queryset(self, request, queryset):
        if self.value() == 'individual':
            return queryset.exclude(user=None)

        if self.value() == 'institution':
            return queryset.exclude(organisation=None)


class SubscriptionJournalListFilter(admin.SimpleListFilter):
    title = _("Abonné à la revue")
    parameter_name = "subscription_journal"

    def lookups(self, request, model_admin):

        journal_ids_list = JournalAccessSubscription.objects.exclude(journals=None).values_list(
            'journals').distinct()

        journal_ids = [v[0] for v in journal_ids_list]

        return (
            (j.code, j.name) for j in Journal.objects.filter(id__in=journal_ids)
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(journals__code=self.value())
        return queryset


class JournalAccessSubscriptionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ('sponsor', ),
        }),
        (_('Bénéficiaire'), {
            'fields': ('user', 'organisation', ),
        }),
        (_('Revue(s) cibles'), {
            'fields': ('journals', 'collection', ),
        }),
    ]

    def get_journal_management_subscription(self, obj):
        if obj.journal_management_subscription:
            return obj.journal_management_subscription.journal
        return ""
    get_journal_management_subscription.short_description = _("Forfait d'abonnement individuel")

    def get_user(self, obj):
        if obj.user:
            return "{} ({})".format(obj.user.username, obj.user.email)
        return ""
    get_user.short_description = _("Utilisateur")

    search_fields = ('organisation__name', 'user__email')
    inlines = [JournalAccessSubscriptionPeriodInline, InstitutionRefererInline]
    filter_horizontal = ('journals',)
    list_display = (
        'pk', 'get_user', 'sponsor', 'organisation', 'get_journal_management_subscription',
    )
    list_display_links = ('pk', 'get_user', 'organisation', )
    list_filter = (SubscriptionTypeListFilter, SubscriptionJournalListFilter)


class JournalManagementPlanAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'max_accounts', 'is_unlimited')

    fieldsets = [
        ('Identification', {
            'fields': (('code', 'title'),),
        }),
        (_('Nombre de comptes'), {
            'fields': (('max_accounts', 'is_unlimited',),),
        }),
    ]


class JournalManagementSubscriptionPeriodInline(admin.TabularInline):
    model = JournalManagementSubscriptionPeriod


class JournalManagementSubscriptionAdmin(admin.ModelAdmin):

    def get_max_accounts(self, obj):
        return obj.plan.max_accounts

    get_max_accounts.short_description = _('Nombre maximum de comptes')

    def get_accounts(self, obj):
        return JournalAccessSubscription.objects.filter(
            journal_management_subscription=obj
        ).count()

    get_accounts.short_description = _("Nombre d'abonnements")

    list_display = ('pk', 'journal', 'plan', 'get_max_accounts', 'get_accounts', 'is_full')
    list_display_links = ('pk', 'journal', )

    inlines = [JournalManagementSubscriptionPeriodInline,]

admin.site.register(InstitutionIPAddressRange, InstitutionIPAddressRangeAdmin)
admin.site.register(JournalAccessSubscription, JournalAccessSubscriptionAdmin)
admin.site.register(JournalAccessSubscriptionPeriod)
admin.site.register(JournalManagementPlan, JournalManagementPlanAdmin)
admin.site.register(JournalManagementSubscription, JournalManagementSubscriptionAdmin)
