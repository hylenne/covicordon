from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from simple_history.models import HistoricalRecords


# Create your models here.
class Member(models.Model):

    first_name = models.CharField(
        max_length=128,
        verbose_name="Nombre",
    )
    last_name = models.CharField(
        max_length=128,
        verbose_name="Apellido",
    )

    phone_number = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name="numero de telefono",
    )

    member_number = models.SmallIntegerField(
        db_index=True,
        verbose_name="numero de socio",
    )

    bedrooms = models.SmallIntegerField(
        default=2,
        validators=[MinValueValidator(2), MaxValueValidator(4)],
        verbose_name="num dormitorios",
    )
    apartment_number = models.SmallIntegerField(
        verbose_name="numero de unidad",
        blank=True,
        null=True,
    )

    history = HistoricalRecords()

    @property
    def total_paid(self):
        total_paid = 0
        for payment in self.payments.all():
            total_paid += payment.ammount
        return total_paid

    @property
    def total_debt(self):
        total_debt = 0
        for debt in self.debts.all():
            total_debt += debt.total
        return total_debt

    class Meta:
        verbose_name = "Socio"
        verbose_name_plural = "Socios"

    def __str__(self):
        return f"{self.member_number} {self.first_name} {self.last_name}"


class DebtAmmend(models.Model):
    name = models.CharField(max_length=128, verbose_name="Motivo")
    member = models.ForeignKey(
        Member, related_name="convenios", on_delete=models.CASCADE
    )
    ammount = models.DecimalField(max_digits=10, decimal_places=2)
    total_payments = models.SmallIntegerField(verbose_name="Total de cuotas")
    due_payments = models.SmallIntegerField(verbose_name="Cuotas cobradas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    @property
    def done(self):
        return (self.total_payments - self.due_payments) == 0

    class Meta:
        verbose_name = "Convenio"


class Debt(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="debts")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    @property
    def total(self):
        total = 0
        for line in self.lines.all():
            total += line.ammount
        return total

    class Meta:
        verbose_name = "Deuda"

    def __str__(self):
        return f"Socio: {self.member.first_name} {self.member.last_name} - Total: {self.total}"


class DebtLine(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
    )
    debt = models.ForeignKey(
        Debt,
        on_delete=models.CASCADE,
        related_name="lines",
    )

    DEBT_TYPES = (
        ("cuota_social", "Cuota social"),
        ("gastos_comunes", "Gastos comunes"),
        ("fondo_socorro", "Fondo socorro"),
        ("atraso_cuota", "Atraso cuota"),
        ("falta_asamblea", "Falta asamblea"),
        ("falta_obra", "Falta obra"),
        ("convenio_social", "Convenio social"),
        ("prestamo_inacoop", "Préstamo inacoop"),
        ("salon_comunal", "Salon comunal"),
        ("salon_otros", "Salon otros"),
        ("saldo_anterior", "Saldo anterior"),
        ("otros", "Otros"),
    )

    type = models.CharField(
        max_length=256,
        choices=DEBT_TYPES,
        verbose_name="tipo",
    )

    @property
    def type_display(self):
        types = {
            "cuota_social": "Cuota social",
            "gastos_comunes": "Gastos comunes",
            "fondo_socorro": "Fondo socorro",
            "atraso_cuota": "Atraso cuota",
            "falta_asamblea": "Falta asamblea",
            "falta_obra": "Falta obra",
            "convenio_social": "Convenio social",
            "prestamo_inacoop": "Préstamo inacoop",
            "salon_comunal": "Salón cominal",
            "salon_otros": "Salon otros",
            "saldo_anterior": "Saldo anterior",
            "otros": "Otros",
        }
        return types[self.type]

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="fecha creación",
    )

    ammount = models.DecimalField(
        verbose_name="monto",
        max_digits=10,
        decimal_places=2,
    )

    description = models.TextField(
        verbose_name="descripción",
        null=True,
        blank=True,
    )

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.member.first_name} {self.member.last_name} {self.ammount}"

    class Meta:
        verbose_name = "Item deuda"
        verbose_name_plural = "Items deuda"


class BankSync(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        c = self.created_at
        return f"Carga realizada: {c.day}/{c.month}/{c.year}"

    class Meta:
        verbose_name = "Carga banco"
        verbose_name_plural = "Cargas banco"


class Payment(models.Model):

    bank_sync = models.ForeignKey(
        BankSync,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="payments",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="fecha de creacion",
    )

    deposited_at = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha de depósito",
    )

    verified = models.BooleanField(default=False, blank=True, verbose_name="verificado")

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
    )

    ammount = models.DecimalField(
        verbose_name="monto",
        max_digits=10,
        decimal_places=2,
    )

    attachment = models.FileField(
        verbose_name="adjunto",
        blank=True,
        null=True,
    )

    reference = models.CharField(max_length=128, verbose_name="num referencia")

    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="notas",
    )

    debt = models.ForeignKey(
        Debt,
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
        verbose_name="deuda",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Pago socio"
        verbose_name_plural = "Pagos socio"


class Config(models.Model):
    ur = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor unidad reajustable",
        default=1621,
    )
    gc = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor gastos comunes",
        default=3500,
    )
    bedroom_price_ur = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio dormitorio en UR",
        default=2.96,
    )
    maintainance_fund = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Fondo de mantenimiento",
        default=0.42,
    )

    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        if self.updated_at:
            date = self.updated_at
            return f"Configuracion al {date.day}/{date.month}/{date.year}"
        return "Configuracion"

    @classmethod
    def get_config(cls):
        config = cls.objects.first()
        if not config:
            config = cls()
            config.save()
        return config
