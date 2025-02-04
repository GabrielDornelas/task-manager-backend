import pytest
from locust import HttpUser, task, between

class TaskManagerUser(HttpUser):
    wait_time = between(1, 2)
    token = None

    def on_start(self):
        response = self.client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_pass"
        })
        self.token = response.json()["token"]

    @task(3)
    def get_tasks(self):
        self.client.get("/task", headers={"Authorization": f"Bearer {self.token}"})

    @task(1)
    def create_task(self):
        self.client.post("/task", 
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "title": "Performance Test Task",
                "description": "Test Description",
                "status": "pending",
                "expire_date": "2024-12-31"
            }
        )
