from django.db import models

# Create your models here.

class Person(models.Model):
	name = models.CharField(max_length=200)
	stature = models.CharField(max_length=6, blank=True)
	usual_host = models.CharField(max_length=128, null=True, blank=True)
		# ALTER TABLE "diet_person" ADD COLUMN "usual_host" varchar(128) NULL;

	class Meta:
	    verbose_name_plural = 'people'

	def __str__(self):
		return self.name


class WeightEntry(models.Model):
	who = models.ForeignKey(Person, on_delete=models.CASCADE)
	date = models.DateField()
	weight = models.FloatField()
	trend = models.FloatField()

	class Meta:
	    verbose_name_plural = 'weight entries'

	def __str__(self):
		return str(self.who) + ' / ' + str(self.date) + ' / ' + str(self.weight)
