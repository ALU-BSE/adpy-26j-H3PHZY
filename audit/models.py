from django.db import models
from django.conf import settings


class GlassLog(models.Model):
	"""Simple audit log for sensitive GET accesses.

	Records who, when, what (model and pk if resolvable), and the endpoint.
	"""
	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	timestamp = models.DateTimeField(auto_now_add=True)

	method = models.CharField(max_length=10)
	path = models.CharField(max_length=1024)

	app_label = models.CharField(max_length=100, blank=True)
	model_name = models.CharField(max_length=100, blank=True)
	object_pk = models.CharField(max_length=255, blank=True)

	extra = models.JSONField(blank=True, null=True)

	class Meta:
		ordering = ['-timestamp']

	def __str__(self):
		parts = [self.path]
		if self.user:
			parts.append(str(self.user))
		return " | ".join(parts)
