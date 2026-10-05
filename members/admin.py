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

<<<<<<< Updated upstream
from .forms import BankSyncForm

=======
>>>>>>> Stashed changes
from members.constants import gen_cuota_social

@admin.action(description="Generar deuda para socios seleccionados")
def generate_debt(modeladmin, request, queryset):

    config = Config.get_config()

    for member in queryset:

        remnant_ammount = member.total_debt - member.total_paid
        if remnant_ammount > 0:
            remnant_ammount *= Decimal(1.1)

        month_debt = Debt(member=member)
        month_debt.save()
<<<<<<< Updated upstream
        # Saldos anteriores
        if remnant_ammount != 0:
            remnants = DebtLine(
                member=member,
                debt=month_debt,
                type="saldo_anterior",
                ammount=remnant_ammount,
            )
            remnants.save()
=======

        remnant_ammount = member.total_debt - member.total_paid

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            debt_ammend.due_payments += 1
            debt_ammend.save()
=======
            debt_ammend.save()
        # Subsidios
        for allowance in [al for al in member.subsidios.all()]:
            al = DebtLine(
                member=member,
                type="subsidio",
                ammount = - allowance.ammount,
                debt=month_debt,
            )
            al.save()


        if Debt.objects.filter(member=member).count()>1:
            payment_deadline = (
                month_debt.created_at - relativedelta(months=1)
                ).date().replace(day=15)

            late_payments = [
                p for p in member.payments.all()
                if p.deposited_at and p.deposited_at > payment_deadline
            ]

            balance_at_15th = remnant_ammount + sum(p.ammount for p in late_payments)
            print(f"balance 15th {balance_at_15th}\nremnant amount {remnant_ammount}")
            
            if balance_at_15th > 10:
                # $10 es el límite a partir del cual se cobra atraso
                print("atraso cuota")
                overdue_tax = DebtLine(
                    member=member,
                    debt=month_debt,
                    type="atraso_cuota",
                    ammount=balance_at_15th * Decimal(0.1),
                )
                overdue_tax.save()


@admin.action(description="Exonerar multa de atraso")
def forgive_overdue(modeladmin, request, queryset):

    config = Config.get_config()

    for member in queryset:
        overdue_fine = DebtLine.objects.filter(
            debt=Debt.objects.filter(member=member).last(),
            member=member,type="atraso_cuota")
        for d in overdue_fine:
            d.delete()
>>>>>>> Stashed changes


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
