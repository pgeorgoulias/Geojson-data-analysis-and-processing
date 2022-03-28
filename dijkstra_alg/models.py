from django.db import models


# Create your models here.

class PortNode(models.Model):
    start = models.CharField(max_length=50)
    end = models.CharField(max_length=50)
    
class Node(models.Model):
    From_Node0 = models.IntegerField()
    Route_Freq = models.FloatField()
    Impedence0 = models.FloatField()
    node_identification = models.TextField()
    To_Node0 = models.IntegerField()
    Name0 = models.TextField()
    Length0= models.FloatField()




