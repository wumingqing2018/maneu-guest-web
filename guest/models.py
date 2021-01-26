from django.db import models


class Order(models.Model):
    order_id = models.CharField(primary_key=True, max_length=16)
    token = models.CharField(max_length=32, blank=True, null=True)
    c_time = models.DateTimeField()
    c_name = models.CharField(max_length=11)
    c_phone = models.CharField(max_length=11)
    frame = models.CharField(max_length=64)
    l_glasses = models.CharField(db_column='L_glasses', max_length=64)  # Field name made lowercase.
    l_pd = models.CharField(db_column='L_pd', max_length=6)  # Field name made lowercase.
    l_add = models.CharField(db_column='L_add', max_length=6)  # Field name made lowercase.
    l_sphere = models.CharField(db_column='L_sphere', max_length=6)  # Field name made lowercase.
    l_deviation = models.CharField(db_column='L_deviation', max_length=6)  # Field name made lowercase.
    l_astigmatic = models.CharField(db_column='L_astigmatic', max_length=6)  # Field name made lowercase.
    r_glasses = models.CharField(max_length=64)
    r_pd = models.CharField(db_column='R_pd', max_length=6)  # Field name made lowercase.
    r_add = models.CharField(db_column='R_add', max_length=6)  # Field name made lowercase.
    r_sphere = models.CharField(db_column='R_sphere', max_length=6)  # Field name made lowercase.
    r_astigmatic = models.CharField(db_column='R_astigmatic', max_length=6)  # Field name made lowercase.
    r_deviation = models.CharField(db_column='R_deviation', max_length=6)  # Field name made lowercase.
    todo = models.CharField(max_length=512)

    class Meta:
        managed = False
        db_table = 'order'