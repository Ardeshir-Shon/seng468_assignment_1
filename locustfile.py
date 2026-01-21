"""
Locust load testing script for the Flask application.
This script simulates user behavior and measures performance under load.
"""

from locust import HttpUser, task, between
import random

class WebAppUser(HttpUser):
    """Simulates a user interacting with the web application."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a simulated user starts."""
        # Seed the database once
        response = self.client.post("/seed")
        if response.status_code == 200:
            print("Database seeded successfully")
    
    @task(3)
    def get_users(self):
        """Get all users - most common operation."""
        self.client.get("/users")
    
    @task(2)
    def get_user(self):
        """Get a specific user."""
        user_id = random.randint(1, 50)
        self.client.get(f"/users/{user_id}")
    
    @task(2)
    def get_posts(self):
        """Get all posts."""
        self.client.get("/posts")
    
    @task(1)
    def get_post(self):
        """Get a specific post."""
        post_id = random.randint(1, 200)
        self.client.get(f"/posts/{post_id}")
    
    @task(1)
    def search_users(self):
        """Search for users - inefficient operation."""
        search_terms = [f"user{random.randint(1, 50)}", "user1", "user10", "user25"]
        query = random.choice(search_terms)
        self.client.get(f"/search?q={query}")
    
    @task(1)
    def heavy_operation(self):
        """CPU-intensive operation."""
        self.client.get("/heavy")
    
    @task(1)
    def create_user(self):
        """Create a new user - tests the inefficient hashing."""
        user_num = random.randint(1000, 9999)
        self.client.post("/users", json={
            "username": f"newuser{user_num}",
            "email": f"newuser{user_num}@example.com",
            "password": "testpassword123"
        })
