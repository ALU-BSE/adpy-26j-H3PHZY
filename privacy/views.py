from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from core.serializers import UserSerializer
from domestic.models import Shipment
from international.models import InternationalShipment
from audit.models import GlassLog

User = get_user_model()


class MyDataView(APIView):
	"""Return all personal data for the authenticated user.

	GET /api/privacy/my-data/

	Response includes:
	- user: basic user info
	- shipments: domestic and international shipments where user is sender
	- audit_logs: entries from GlassLog for this user
	- consent_history: placeholder list (no consent model present)
	"""
	permission_classes = [IsAuthenticated]

	def get(self, request):
		user = request.user

		user_data = UserSerializer(user).data

		domestic_qs = Shipment.objects.filter(sender=user).order_by('-created_at')
		intl_qs = InternationalShipment.objects.filter(sender=user).order_by('-created_at')

		shipments = {
			'domestic': [
				{
					'tracking_number': s.tracking_number,
					'status': s.status,
					'recipient_name': s.recipient_name,
					'recipient_phone': s.recipient_phone,
					'created_at': s.created_at,
					'updated_at': s.updated_at,
				}
				for s in domestic_qs
			],
			'international': [
				{
					'tracking_number': s.tracking_number,
					'status': s.status,
					'recipient_name': s.recipient_name,
					'recipient_phone': s.recipient_phone,
					'sender_tin': s.sender_tin,
					'recipient_tin': s.recipient_tin,
					'created_at': s.created_at,
					'updated_at': s.updated_at,
				}
				for s in intl_qs
			]
		}

		audit_qs = GlassLog.objects.filter(user=user).order_by('-timestamp')[:100]
		audit_logs = [
			{
				'timestamp': a.timestamp,
				'method': a.method,
				'path': a.path,
				'app_label': a.app_label,
				'model_name': a.model_name,
				'object_pk': a.object_pk,
				'extra': a.extra,
			}
			for a in audit_qs
		]

		# Consent history: no model found in repo; return empty list for now
		consent_history = []

		return Response({
			'user': user_data,
			'shipments': shipments,
			'audit_logs': audit_logs,
			'consent_history': consent_history,
		}, status=status.HTTP_200_OK)
