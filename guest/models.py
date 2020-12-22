# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Order(models.Model):
    order_id = models.CharField(primary_key=True, max_length=16)
    c_time = models.DateTimeField()
    c_name = models.CharField(max_length=11)
    c_phone = models.CharField(max_length=11)
    u_time = models.DateTimeField()
    u_name = models.CharField(max_length=11)
    u_phone = models.CharField(max_length=11)
    frame = models.CharField(max_length=20, blank=True, null=True)
    l_glasses = models.CharField(max_length=20, blank=True, null=True)
    l_sphere = models.CharField(max_length=5, blank=True, null=True)
    l_astigmatic = models.CharField(max_length=5, blank=True, null=True)
    l_deviation = models.CharField(max_length=5, blank=True, null=True)
    l_add = models.CharField(max_length=5, blank=True, null=True)
    l_pd = models.CharField(max_length=2, blank=True, null=True)
    r_glasses = models.CharField(max_length=20, blank=True, null=True)
    r_sphere = models.CharField(max_length=5, blank=True, null=True)
    r_astigmatic = models.CharField(max_length=5, blank=True, null=True)
    r_deviation = models.CharField(max_length=5, blank=True, null=True)
    r_add = models.CharField(max_length=5, blank=True, null=True)
    r_pd = models.CharField(max_length=2, blank=True, null=True)
    token = models.CharField(max_length=32, blank=True, null=True)
    todo = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order'
