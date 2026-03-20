from locust import HttpUser, task, between

class IshemaLinkLoadTester(HttpUser):
    wait_time = between(1, 2)
    
    def on_start(self):
        """Perform login if necessary"""
        pass

    @task(3)
    def check_health(self):
        self.client.get("/api/v1/status/")

    @task(2)
    def view_pricing(self):
        self.client.get("/api/v1/pricing/tariffs/")

    @task(1)
    def track_shipment(self):
        # Using a mock tracking code
        self.client.get("/api/v1/shipments/RW-TEST123/live/")

    @task(1)
    def admin_dashboard(self):
        # Simulate admin checking the control tower
        self.client.get("/api/v1/admin/dashboard/summary/")
