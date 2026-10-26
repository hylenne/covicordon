from decimal import Decimal

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Member,
    Debt,
    DebtLine,
    DebtAmmend,
    Config,
    Payment,
    BankSync,
)

from .forms import BankSyncForm

from members.constants import gen_cuota_social


@admin.action(description="generar deuda para socios seleccionados")
def generate_debt(modeladmin, request, queryset):

    config = Config.get_config()

    for member in queryset:

        remnant_ammount = member.total_debt - member.total_paid
        if remnant_ammount > 0:
            remnant_ammount *= Decimal(1.1)

        month_debt = Debt(member=member)
        month_debt.save()
        # Saldos anteriores
        if remnant_ammount != 0:
            remnants = DebtLine(
                member=member,
                debt=month_debt,
                type="saldo_anterior",
                ammount=remnant_ammount,
            )
            remnants.save()
        # Cuota social
        cuota_social = DebtLine(
            member=member,
            type="cuota_social",
            ammount=gen_cuota_social(member),
            debt=month_debt,
        )
        # Gastos comunes
        gastos_comunes = DebtLine(
            member=member,
            type="gastos_comunes",
            ammount=config.gc,
            debt=month_debt,
        )
        for debt in [cuota_social, gastos_comunes]:
            debt.save()
        # Convenios activos si tiene
        for debt_ammend in [da for da in member.convenios.all() if not da.done]:
            debt = DebtLine(
                member=member,
                type="convenio_social",
                ammount=debt_ammend.ammount,
                description=debt_ammend.name,
                debt=month_debt,
            )
            debt.save()
            debt_ammend.due_payments += 1
            debt_ammend.save()


@admin.register(DebtAmmend)
class DebtAmmendAdmin(admin.ModelAdmin):
    list_display = [
        "member",
        "ammount",
        "total_payments",
        "due_payments",
    ]
    autocomplete_fields = ["member"]
    search_fields = ["member"]


@admin.register(BankSync)
class BankSyncAdmin(admin.ModelAdmin):

    list_display = ["created_at"]
    form = BankSyncForm


@admin.register(Payment)
class PaymentAdmin(SimpleHistoryAdmin):

    list_display = [
        "deposited_at",
        "member",
        "ammount",
        "verified",
    ]
    autocomplete_fields = ["member"]
    search_fields = ["member"]


@admin.register(Member)
class MemberAdmin(SimpleHistoryAdmin):
    list_display = [
        "member_number",
        "first_name",
        "last_name",
    ]

    search_fields = ["member_number", "first_name", "last_name"]

    actions = [generate_debt]


@admin.register(DebtLine)
class DebtLineAdmin(SimpleHistoryAdmin):
    list_display = [
        "member",
        "type",
        "ammount",
        "created_at",
    ]

    sortable_by = [
        "member",
        "type",
        "created_at",
    ]

    list_filter = [
        "member",
        "type",
    ]


class DebtLineInline(admin.StackedInline):
    model = DebtLine
    search_fields = ["member"]
    autocomplete_fields = ["member"]
    extra = 0


@admin.register(Debt)
class DebtAdmin(SimpleHistoryAdmin):
    list_display = [
        "member",
        "total",
    ]
    search_fields = ["member"]
    autocomplete_fields = ["member"]
    inlines = [DebtLineInline]


admin.site.index_title = "Bienvenido a la administracion de Covicordon"
admin.site.site_header = "Administracion de Covicordon"
admin.site.site_title = "Administracion de Covicordon"

admin.site.register(Config)
