# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import uuid

from django.db import models


class ManeuAdmin(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid1, editable=False)
    username = models.CharField(max_length=36)
    password = models.CharField(max_length=36)
    nickname = models.CharField(max_length=36)
    email = models.CharField(max_length=36)
    phone = models.CharField(max_length=36)
    level = models.CharField(max_length=36)
    state = models.CharField(max_length=36)
    time = models.DateTimeField(blank=True, null=True)
    content = models.CharField(max_length=512, blank=True, null=True)
    location = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'maneu_admin'
        unique_together = (('id', 'username'),)


class ManeuGuess(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid1, editable=False)
    admin_id = models.CharField(max_length=36, blank=True, null=True)
    time = models.DateTimeField()
    name = models.CharField(max_length=36, blank=True, null=True)
    phone = models.CharField(max_length=36, blank=True, null=True)
    sex = models.CharField(max_length=36, blank=True, null=True)
    age = models.CharField(max_length=36, blank=True, null=True)
    ot = models.CharField(db_column='OT', max_length=36, blank=True, null=True)  # Field name made lowercase.
    em = models.CharField(db_column='EM', max_length=36, blank=True, null=True)  # Field name made lowercase.
    dfh = models.CharField(db_column='DFH', max_length=36, blank=True, null=True)  # Field name made lowercase.
    remark = models.TextField()

    class Meta:
        managed = False
        db_table = 'maneu_guess'


class ManeuOrder(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid1, editable=False)
    time = models.DateTimeField()
    name = models.CharField(max_length=36)
    phone = models.CharField(max_length=36)
    guess_id = models.CharField(max_length=36)
    admin_id = models.CharField(max_length=36)
    store_id = models.CharField(max_length=36)
    vision_id = models.CharField(max_length=36)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'maneu_order'


class ManeuOrderV2(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid1, editable=False)
    time = models.DateTimeField()
    name = models.CharField(max_length=36)
    phone = models.CharField(max_length=36)
    guess_id = models.CharField(max_length=36)
    admin_id = models.CharField(max_length=36)
    store_id = models.CharField(max_length=36)
    vision_id = models.CharField(db_column='vision_id', max_length=36)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'maneu_order'


class ManeuService(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid1, editable=False)
    time = models.DateTimeField()
    admin_id = models.CharField(max_length=36)
    guess_id = models.CharField(max_length=36)
    order_id = models.CharField(db_column='order_id', max_length=36, blank=True,
                                null=True)  # Field name made lowercase.
    content = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'maneu_service'


class ManeuStore(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid1, editable=False)
    time = models.DateTimeField()
    order_id = models.CharField(db_column='order_id', max_length=36)  # Field name made lowercase.
    admin_id = models.CharField(max_length=36)
    guess_id = models.CharField(db_column='guess_id', max_length=36)  # Field name made lowercase.
    content = models.TextField()

    class Meta:
        managed = False
        db_table = 'maneu_store'


class ManeuRefraction(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid1, editable=False)
    admin_id = models.CharField(max_length=36)
    guess_id = models.CharField(db_column='guess_id', max_length=36)  # Field name made lowercase.
    time = models.DateTimeField()
    content = models.TextField()

    class Meta:
        managed = False
        db_table = 'maneu_refraction'


class ManeuVision(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid1, editable=False)
    admin_id = models.CharField(max_length=36)
    guess_id = models.CharField(db_column='guess_id', max_length=36)  # Field name made lowercase.
    time = models.DateTimeField()
    content = models.TextField()

    class Meta:
        managed = False
        db_table = 'maneu_vision'
